#!/bin/bash

# === Configuration ===
DUMP_FILE_NAME="Metadata_Restore.dump"
SOURCE_POD="postgres-replica-cluster-s3-1"
TARGET_POD="ibm-lh-postgres-edb-1"
NAMESPACE="cpd-instance"
DB_NAME="iceberg_catalog"
DB_USER="postgres"
DUMP_PATH="/var/lib/postgresql/data/pgdata/${DUMP_FILE_NAME}"

# === Table List ===
TABLES=(
  "CDS"
  "CTLGS"
  "SDS"
  "SD_PARAMS"
  "SERDES"
  "SERDE_PARAMS"
  "DBS"
  "DATABASE_PARAMS"
  "TBLS"
  "TABLE_PARAMS"
  "TAB_COL_STATS"
  "TBL_PRIVS"
  "DB_PRIVS"
  "COLUMNS_V2"
  "BUCKETING_COLS"
  "SORT_COLS"
  "PARTITIONS"
  "PARTITION_PARAMS"
  "PARTITION_KEYS"
  "PARTITION_KEY_VALS"
  "PART_COL_STATS"
  "FUNCS"
  "FUNC_RU"
  "HIVE_LOCKS"
  "NEXT_LOCK_ID"
  "RUNTIME_STATS"
  "KEY_CONSTRAINTS"
  "SEQUENCE_TABLE"
)

# === Step 1: Dump selected tables from source pod ===
echo "Dumping tables from source pod..."
DUMP_CMD="pg_dump -U ${DB_USER} -d ${DB_NAME} -F c"
for table in "${TABLES[@]}"; do
  DUMP_CMD+=" -t '\"${table}\"'"
done
DUMP_CMD+=" -f ${DUMP_PATH}"

oc exec -it "${SOURCE_POD}" -n "${NAMESPACE}" -- bash -c "${DUMP_CMD}"

# === Step 2: Copy dump file to local ===
echo "Copying dump file from source pod to local..."
oc cp "${NAMESPACE}/${SOURCE_POD}:${DUMP_PATH}" "./${DUMP_FILE_NAME}"

# === Step 3: Copy dump file to target pod ===
echo "Copying dump file from local to target pod..."
oc cp "./${DUMP_FILE_NAME}" "${NAMESPACE}/${TARGET_POD}:${DUMP_PATH}"

# === Step 4: Drop all target tables with CASCADE ===
echo "Dropping existing tables in target database..."
DROP_SQL="DROP TABLE IF EXISTS "
for table in "${TABLES[@]}"; do
  DROP_SQL+="\"${table}\", "
done
# Trim trailing comma and space, then add CASCADE and semicolon
DROP_SQL="${DROP_SQL%, } CASCADE;"

oc exec -it "${TARGET_POD}" -n "${NAMESPACE}" -- \
  psql -U "${DB_USER}" -d "${DB_NAME}" -c "${DROP_SQL}"

# === Step 5: Restore dump inside target pod ===
echo "Restoring dump file into target database..."
oc exec -it "${TARGET_POD}" -n "${NAMESPACE}" -- \
  pg_restore -U "${DB_USER}" -d "${DB_NAME}" -F c "${DUMP_PATH}"

echo "✅ Sync complete using dump file: ${DUMP_FILE_NAME}"
