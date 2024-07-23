from pyspark.sql import SparkSession
import os
import pyspark
from datetime import datetime
def init_spark():
    #  watsonx.data access key
    #  CPD base64{<instanceid>|ZenAPIkey base64{username:<apikey>}}
    #  SaaS base64{<crn>|Basic base64{ibmlhapikey_<user_id>:<IAM_APIKEY>}}
    #  Current only support spark.hadoop.fs.s3a.path.style.access
    spark = SparkSession.builder.appName("test") \
             .config("spark.hadoop.fs.s3a.endpoint", "<watsonx.data das endpoint>/cas/v1/proxy")\
             .config("spark.hadoop.fs.s3a.access.key","<watsonx.data access key>")\
             .config("spark.hadoop.fs.s3a.secret.key", "anystring")\
             .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")\
             .config("spark.hadoop.fs.s3a.path.style.access", "true") \
             .config("spark.executor.extraClassPath","<Download Jar folder>/hive-common-2.3.9.jar:<Download Jar folder>/hive-metastore-2.3.9.jar:<Download Jar folder>/iceberg-spark-runtime-3.4_2.12-1.4.0.jar") \
             .config("spark.driver.extraClassPath","<Download Jar folder>/hive-common-2.3.9.jar:<Download Jar folder>/hive-metastore-2.3.9.jar:<Download Jar folder>/iceberg-spark-runtime-3.4_2.12-1.4.0.jar") \
             .config("spark.hive.metastore.client.plain.username","<CPD user has metastore access>") \
             .config("spark.hive.metastore.client.plain.password","<CPD user password>") \
             .config("spark.hive.metastore.client.auth.mode","PLAIN") \
             .config("spark.hive.metastore.truststore.password","changeit") \
             .config("spark.hive.metastore.truststore.path","/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/lib/security/cacerts") \
             .config("spark.hive.metastore.truststore.type","JKS") \
             .config("spark.hive.metastore.uris","<HMS endpoint please get from infrastruture management UI >") \
             .config("spark.hive.metastore.use.SSL","true") \
             .config("spark.sql.extensions","org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
             .config("spark.sql.catalog.<catalog name in watsonx.data>","org.apache.iceberg.spark.SparkCatalog") \
             .config("spark.sql.catalog.<catalog name in watsonx.data>.type","hive") \
             .config("spark.sql.catalogImplementation","hive") \
             .config("spark.sql.iceberg.vectorization.enabled","false") \
             .enableHiveSupport().getOrCreate()
    return spark

def create_database(spark,bucket_name,catalog,databasename):
    spark.sql(f"create database if not exists {catalog}.{databasename} LOCATION 's3a://{bucket_name}/{databasename}'")

def show_databases(spark,catalog):
    spark.sql(f"show databases from {catalog}").show()
    
def list_databases(spark,catalog):
    # list the database under lakehouse catalog
    spark.sql(f"show databases from {catalog}").show()
def basic_iceberg_table_operations(spark,catalog,databasename,tablename):
    # demonstration: Create a basic Iceberg table, insert some data and then query table
    print("creating table")
    spark.sql(f"create table if not exists {catalog}.{databasename}.{tablename}(id INTEGER, name VARCHAR(10), age INTEGER, salary DECIMAL(10, 2)) using iceberg").show()
    print("table created")

def insert_data(spark,catalog,schema,table):
    print("=======insert data======== ")
    sqlDF = spark.sql(f"insert into {catalog}.{schema}.{table} values(1,'aa',18,12000)")
    
def view_data(spark,catalog,schema,table):
    print("=======query data======== ")
    sqlDF = spark.sql(f"select * from {catalog}.{schema}.{table}")
    sqlDF.show()

def list_tables(spark,catalog,schema):
    # list the database under lakehouse catalog
    spark.sql(f"show tables from {catalog}.{schema}").show()

def main():
    try:
        spark = init_spark()
        spark.sparkContext.setLogLevel("INFO")
        show_databases(spark,"<my catalog>")
        create_database(spark,"<my bucket>","<my catalog>","<schema>")
        basic_iceberg_table_operations(spark,"<my catalog>","<schema>","<table>")
        list_tables(spark,"<my catalog>","<schema>")
        insert_data(spark,"<my catalog>","<schema>","<table>")
        view_data(spark,"<my catalog>","<schema>","<table>")
        
        
    finally:
        spark.sparkContext.stop()
        spark.stop()
if __name__ == '__main__':
    main()
