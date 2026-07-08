#!/usr/bin/env python3
"""
patch_iceberg_avro.py
---------------------
Patches stale hdfs:// paths inside local Iceberg Avro manifest files,
BEFORE uploading to Ceph/S3.

Handles both:
  - Manifest files (*-m0.avro): rewrites file_path strings, captures new byte sizes
  - Manifest list files (snap-*.avro): rewrites manifest_path strings AND updates
    manifest_length to match the new byte size of the rewritten manifest files

Must be run AFTER rewriting .metadata.json files with sed, and BEFORE uploading to Ceph.

Usage:
    pip install fastavro

    python3 patch_iceberg_avro.py \\
      --table-dir /root/<staging_dir>/<table_name> \\
      --old-prefix "hdfs://<HDFS_NAMENODE>/<hdfs_table_path>" \\
      --new-prefix "s3a://<YOUR_BUCKET_NAME>/<destination_path>/<table_name>"
"""

import argparse
import io
import sys
import fastavro
from pathlib import Path


def patch_value(v, old, new):
    """Recursively replace old prefix with new in all string fields."""
    if isinstance(v, str):
        return v.replace(old, new)
    elif isinstance(v, dict):
        return {k: patch_value(val, old, new) for k, val in v.items()}
    elif isinstance(v, list):
        return [patch_value(item, old, new) for item in v]
    return v


def patch_snap_record(record, old, new, transformed_sizes):
    """
    Patch a manifest list (snap-*.avro) record.
    Rewrites manifest_path AND updates manifest_length to the new file size.
    """
    if not isinstance(record, dict):
        return record

    result = {}
    for key, value in record.items():
        if isinstance(value, str):
            result[key] = value.replace(old, new)
        elif key == 'manifest_length' and isinstance(value, int):
            # Look up new size of the already-patched manifest file
            manifest_path = record.get('manifest_path', '')
            filename = Path(manifest_path).name
            new_size = transformed_sizes.get(filename)
            if new_size is not None and new_size != value:
                print(f'    manifest_length: {filename}  {value} → {new_size} bytes')
                result[key] = new_size
            else:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = patch_value(value, old, new)
        elif isinstance(value, list):
            result[key] = patch_value(value, old, new)
        else:
            result[key] = value
    return result


def rewrite_avro_file(path: Path, record_fn) -> int:
    """Read, transform, and overwrite a local Avro file. Returns new byte size."""
    raw = path.read_bytes()
    reader = fastavro.reader(io.BytesIO(raw))
    schema = reader.writer_schema
    records = list(reader)

    # Preserve original Avro codec
    codec = 'deflate'
    if reader.metadata:
        raw_codec = reader.metadata.get(b'avro.codec') or reader.metadata.get('avro.codec')
        if isinstance(raw_codec, bytes):
            raw_codec = raw_codec.decode('utf-8', errors='ignore')
        if raw_codec and raw_codec.strip():
            codec = raw_codec.strip()

    transformed = [record_fn(r) for r in records]

    out = io.BytesIO()
    try:
        fastavro.writer(out, schema, transformed, codec=codec)
    except Exception:
        # Fallback: write without specifying codec
        out = io.BytesIO()
        fastavro.writer(out, schema, transformed)

    data = out.getvalue()
    path.write_bytes(data)
    return len(data)


def main():
    parser = argparse.ArgumentParser(
        description='Patch hdfs:// paths in Iceberg Avro manifest files before uploading to Ceph.'
    )
    parser.add_argument('--table-dir', required=True,
                        help='Local path to the table directory (contains data/ and metadata/)')
    parser.add_argument('--old-prefix', required=True,
                        help='HDFS path prefix to replace, e.g. hdfs://namenode:8020/warehouse/.../table')
    parser.add_argument('--new-prefix', required=True,
                        help='S3A path prefix to replace with, e.g. s3a://bucket/warehouse/.../table')
    args = parser.parse_args()

    old = args.old_prefix
    new = args.new_prefix

    metadata_dir = Path(args.table_dir) / 'metadata'
    if not metadata_dir.exists():
        print(f'ERROR: metadata directory not found: {metadata_dir}')
        sys.exit(1)

    avro_files = sorted(metadata_dir.glob('*.avro'))
    manifest_files = [f for f in avro_files if not f.name.startswith('snap-')]
    snap_files     = [f for f in avro_files if f.name.startswith('snap-')]

    print(f'Table dir  : {args.table_dir}')
    print(f'Old prefix : {old}')
    print(f'New prefix : {new}')
    print(f'Found      : {len(manifest_files)} manifest file(s), {len(snap_files)} manifest list file(s)\n')

    # Step 1 — patch manifest files first, capture new sizes
    transformed_sizes = {}
    for path in manifest_files:
        print(f'Patching manifest: {path.name}')
        new_size = rewrite_avro_file(path, lambda r: patch_value(r, old, new))
        transformed_sizes[path.name] = new_size
        print(f'  Done — new size: {new_size} bytes')

    # Step 2 — patch manifest list files, updating manifest_length
    for path in snap_files:
        print(f'Patching manifest list: {path.name}')
        rewrite_avro_file(path, lambda r: patch_snap_record(r, old, new, transformed_sizes))
        print(f'  Done')

    print(f'\n✓ All {len(avro_files)} Avro files patched in place.')
    print(f'  You can now upload the full table directory to Ceph.')


if __name__ == '__main__':
    main()
