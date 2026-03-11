# WXD - Confluent Tableflow Integration

This tutorial demonstrates how to integrate IBM watsonx.data with Confluent Tableflow to read data from Confluent-managed Iceberg tables using Apache Spark.

## What This Does

The [`read_confluent_table_standalone.py`](read_confluent_table_standalone.py:1) script provides a complete solution for:

- **Connecting to Confluent Tableflow**: Establishes a connection to Confluent's REST catalog using API credentials
- **Auto-Discovery**: Automatically discovers available namespaces (schemas) and tables in the catalog
- **Table Inspection**: Describes table schemas and displays metadata
- **Data Querying**: Retrieves and displays sample data from Confluent Tableflow tables
- **Standalone Execution**: Runs independently with embedded Spark configuration

## Prerequisites

- Apache Spark with Iceberg support
- PySpark installed
- Confluent Tableflow API credentials (API key and secret)
- Access to a Confluent Tableflow catalog

## Configuration

### Storage Authentication Options

#### Option 1: Confluent Managed Storage (Recommended)

For **Confluent Managed Storage**, no additional storage configuration is required. The storage is automatically authenticated using the same API key provided in the catalog credentials:

```python
.config("spark.sql.catalog.tableflowdemo.credential", "<apikey>:<secret>")
```

#### Option 2: Integrated AWS S3 Storage

For **integrated AWS S3 storage** with TableFlow, you need to add the following additional configurations to connect to the storage:

```python
.config("spark.sql.catalog.tableflowdemo.s3.access-key-id", "<s3-accesskey>")
.config("spark.sql.catalog.tableflowdemo.s3.secret-access-key", "<s3-secretkey>")
.config("spark.sql.catalog.tableflowdemo.s3.region", "<s3-region>")
```

> **Note**: `tableflowdemo` is a local alias for Spark to consume the catalog. You can use any name you prefer for this alias.

## Usage

### Step 1: Update Configuration

Edit the script to add your Confluent credentials:
```python
.config("spark.sql.catalog.tableflowdemo.uri", "<rest-catalog-uri>")
.config("spark.sql.catalog.tableflowdemo.credential", "<apikey>:<secret>")
```

### Step 2: Run the PySpark Script

You can run the PySpark script in three different ways:

#### Option 1: Using SparkLab (VS Code Development Environment)

Use IBM watsonx.data's SparkLab for interactive development and testing:

- **Documentation**: [VS Code Development Environment - Spark Labs](https://www.ibm.com/docs/en/watsonxdata/standard/2.3.x?topic=experience-vs-code-development-environment-spark-labs)
- **Benefits**: Interactive development, debugging support, immediate feedback
- **Best For**: Development, testing, and iterative refinement

#### Option 2: Submit Spark Application using REST API

Submit the application programmatically using the Spark Application API:

- **Documentation**: [Submitting Spark Application by using REST API](https://www.ibm.com/docs/en/watsonxdata/standard/2.3.x?topic=engine-submitting-spark-application-by-using-rest-api)
- **Benefits**: Automation, integration with CI/CD pipelines, programmatic control
- **Best For**: Production deployments, automated workflows

#### Option 3: Submit Spark Application using CPDCTL CLI

Submit the application using the CPDCTL CLI interface:

- **Documentation**: [Submitting Spark Application by using CPDCTL](https://www.ibm.com/docs/en/watsonxdata/standard/2.3.x?topic=engine-submitting-spark-application-by-using-cpdctl)
- **Benefits**: Command-line convenience, scriptable, easy integration with shell scripts
- **Best For**: Manual submissions, shell script automation, DevOps workflows

### Expected Output

The script will:
- Display all available namespaces in the catalog
- List all tables in the first namespace
- Show the schema of the first table
- Display row count and sample data (first 20 rows)


## Configuration Parameters

| Parameter | Description |
|-----------|-------------|
| `spark.sql.catalog.tableflowdemo` | Catalog implementation (Iceberg Spark Catalog) |
| `spark.sql.catalog.tableflowdemo.type` | Catalog type (REST) |
| `spark.sql.catalog.tableflowdemo.uri` | REST catalog endpoint URL |
| `spark.sql.catalog.tableflowdemo.credential` | API key and secret in format `apikey:secret` |
| `spark.sql.catalog.tableflowdemo.io-impl` | File I/O implementation (S3FileIO) |
| `spark.sql.catalog.tableflowdemo.client.region` | AWS region for the catalog |
| `spark.sql.catalog.tableflowdemo.s3.remote-signing-enabled` | Enable remote signing for S3 operations |

## Troubleshooting

- **Authentication Errors**: Verify your API key and secret are correct
- **Connection Issues**: Check the REST catalog URI and network connectivity
- **Region Mismatch**: Ensure the region configuration matches your Confluent setup
- **S3 Access Issues**: If using integrated S3 storage, verify your S3 credentials and region

## Additional Resources

- [Confluent Tableflow Documentation](https://docs.confluent.io/cloud/current/topics/tableflow/overview.html#tableflow-in-ccloud)
- [IBM watsonx.data Documentation](https://www.ibm.com/docs/en/watsonxdata)