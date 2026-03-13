"""
This module reads data from a Confluent Tableflow Iceberg table
with embedded Spark configuration for standalone execution.

Usage:
    spark-submit read_confluent_table_standalone.py
"""

import json
from pyspark.sql import SparkSession


def escape_name(name: str) -> str:
    """Escape table/schema names with backticks."""
    return f"`{name}`"


def create_spark_session_with_confluent_config() -> SparkSession:
    """
    Create Spark session with Confluent Tableflow configuration embedded.
    
    Returns:
        SparkSession: Configured Spark session with Confluent Tableflow catalog
    """
    spark = (
        SparkSession.builder
        .appName("Read Confluent Tableflow Table")
        .config("spark.sql.catalog.tableflowdemo", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.tableflowdemo.type", "rest")
        .config("spark.sql.catalog.tableflowdemo.uri",
                "https://tableflow.{CLOUD_REGION}.aws.confluent.cloud/iceberg/catalog/organizations/{ORG_ID}/environments/{ENV_ID}")
        .config("spark.sql.catalog.tableflowdemo.credential",
                "<apikey>:<secret>")
        .config("spark.sql.catalog.tableflowdemo.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .config("spark.sql.catalog.tableflowdemo.rest-metrics-reporting-enabled", "false")
        .config("spark.sql.catalog.tableflowdemo.s3.remote-signing-enabled", "true")
        .config("spark.sql.catalog.tableflowdemo.client.region", "{CLOUD_REGION}")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .getOrCreate()
    )
    
    print("\n" + "="*100)
    print("SPARK SESSION CREATED WITH CONFLUENT TABLEFLOW CONFIGURATION")
    print("="*100)
    print(f"Catalog: tableflowdemo")
    print(f"Region: us-east-1")
    print(f"Catalog Type: Iceberg REST")
    print("="*100 + "\n")
    
    return spark


def read_and_display_table(spark: SparkSession, catalog: str) -> None:
    """
    Read and display table contents in human-readable format.
    Automatically discovers namespaces and tables, then queries the first available table.
    
    Args:
        spark: SparkSession instance
        catalog: Catalog name (e.g., "tableflowdemo")
    """
    try:
        print("\n" + "="*100)
        print(f"READING CONFLUENT TABLEFLOW CATALOG: {catalog}")
        print("="*100)
        
        # Display and store available namespaces (schemas)
        print("\n=== Available Namespaces ===")
        namespaces_df = spark.sql(f"SHOW NAMESPACES IN {catalog}")
        namespaces_df.show(truncate=False)
        
        # Get the first namespace
        namespaces = namespaces_df.collect()
        if not namespaces:
            print(f"No namespaces found in catalog '{catalog}'")
            return
        
        # Strip backticks if they exist in the namespace value
        first_namespace = namespaces[0]['namespace'].strip('`')
        print(f"\nUsing first namespace: {first_namespace}")
        
        # Display and store available tables in the first namespace
        print(f"\n=== Tables in {catalog}.`{first_namespace}` ===")
        tables_df = spark.sql(f"SHOW TABLES IN {catalog}.`{first_namespace}`")
        tables_df.show(truncate=False)
        
        # Get the first table
        tables = tables_df.collect()
        if not tables:
            print(f"No tables found in namespace '{first_namespace}'")
            return
        
        first_table = tables[0]['tableName']
        print(f"\nUsing first table: {first_table}")
        
        # Now query the first table
        schema = first_namespace
        table = first_table
        
        # Describe the table schema
        print(f"\n=== Describe Table: {catalog}.`{schema}`.{table} ===")
        spark.sql(f"DESCRIBE TABLE {catalog}.`{schema}`.{table}").show(truncate=False)
        
        # Get row count
        print(f"\n=== Row Count ===")
        row_count = spark.sql(f"SELECT COUNT(*) as count FROM {catalog}.`{schema}`.{table}").collect()[0]['count']
        print(f"Total rows: {row_count}")
        
        # Query the Iceberg table
        print(f"\n=== Sample Data (First 20 Rows) ===")
        spark.sql(f"SELECT * FROM {catalog}.`{schema}`.{table}").show(n=20, truncate=False)
        
        print("\n" + "="*100)
        print(f"SUMMARY: Successfully queried {catalog}.{schema}.{table}")
        print(f"Total rows in table: {row_count}")
        print("="*100 + "\n")
        
    except Exception as e:
        print(f"\nERROR reading table: {e}\n")
        raise


def main():
    """
    Main function to read and display Confluent Tableflow table.
    Automatically discovers and queries the first available table.
    """
    spark = None
    
    try:
        # Configuration - The catalog name from Spark config
        catalog = "tableflowdemo"
        
        print("\n" + "="*100)
        print("CONFLUENT TABLEFLOW READER - STANDALONE MODE")
        print("="*100)
        print(f"Catalog: {catalog}")
        print("="*100 + "\n")
        
        # Create Spark session with embedded configuration
        spark = create_spark_session_with_confluent_config()
        
        # Read and display table (auto-discovers first namespace and table)
        read_and_display_table(spark, catalog)
        
    except Exception as e:
        print(f"\nError during table read: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if spark:
            print("\nStopping Spark session...")
            spark.stop()
            print("Spark session stopped.\n")


if __name__ == "__main__":
    main()

# Made with Bob
