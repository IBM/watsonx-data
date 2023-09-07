
- [Configuring Apache Spark for IBM WatsonX.Data](#configuring-apache-spark-for-ibm-watsonxdata)
- [Connect to lakehouse using spark-sql utility](#connect-to-lakehouse-using-spark-sql-utility)
- [Connect to lakehouse using pyspark](#connect-to-lakehouse-using-pyspark)
- [Simple data operations/transformations with PySpark](#simple-data-operationstransformations-with-pyspark)
- [Frequence Pattern Growth - Data Mining](#frequence-pattern-growth---data-mining)
- [Writing to the IBM Lakehouse](#writing-to-the-ibm-lakehouse)


## Configuring Apache Spark for IBM WatsonX.Data
Apache Spark properties can be set/changed in one of many ways including:
- Updating the spark-default.conf file
- Passing one or more spark configuration values at runtime using the --conf parameter-name=parameter-value
- Programmatically updating the SparkConfig as part of the SparkContext.

For the purpose of this lab, we will use the spark-defaults.conf file. The spark-defaults.conf has been pre-configured for connectivity to IBM Lakehouse using Thrift protocol. We will simply inspect the /opt/spark/conf/spark-defaults.conf file. There are 3 main groups of parameters 

**Note: Nothing to change**
- Hive metastore connectivity parameters
  - spark.sql.catalog.lakehouse.uri
  - spark.hive.metastore.client.plain.username
  - spark.hive.metastore.client.plain.password
- Truststore parameters
  - spark.hive.metastore.truststore.type
  - spark.hive.metastore.truststore.path
  - spark.hive.metastore.truststore.password
- Object store parameters
  - spark.hadoop.fs.s3a.bucket.iceberg-bucket.endpoint
  - spark.hadoop.fs.s3a.bucket.iceberg-bucket.access.key
  - spark.hadoop.fs.s3a.bucket.iceberg-bucket.secret.key

## Connect to lakehouse using spark-sql utility
Spark SQL is a very important and most used module that is used for structured data processing.

1. Connect to specific spark catalog
In the spark-defaults.conf file we say the use of lakehouse as the name for the Iceberg Spark catalog so we will need to connect to that catalog.

```console
❯ spark-sql

23/09/06 00:39:16 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Spark master: local[*], Application Id: local-1693985957696

spark-sql> use lakehouse;
Time taken: 1.479 seconds
spark-sql> 
```
2. Inspect available schemas

```
spark-sql> show schemas;
23/09/06 00:49:48 WARN HiveConf: HiveConf of name hive.metastore.truststore.type does not exist
default
example_03
example_04
example_05
techxchange
Time taken: 0.353 seconds, Fetched 5 row(s)
spark-sql> 
```


## Connect to lakehouse using pyspark
PyASpark gives you the flexibility to leverage the Python modules and more importantly the Dataframe API. Upon writing your PySpark-based pipeline, one can chose to execute and scale the pipeline with Apache Spark anywhere.

Note: The spark configuration that we setup earlier applies to both spark-sql and pyspark unless you want to deliberately change some configuration parameters programmatically.

1. Create PySpark dataframe
````
>>> customer_df=spark.read.table("lakehouse.example_03.customer")
23/09/07 09:54:36 WARN HiveConf: HiveConf of name hive.metastore.truststore.type does not exist
23/09/07 09:54:36 WARN MetricsConfig: Cannot locate configuration: tried hadoop-metrics2-s3a-file-system.properties,hadoop-metrics2.properties
````

2. Inspect contents of PySpark dataframe (metadata, data)

```
>>> customer_df.schema
StructType([StructField('custkey', LongType(), True), StructField('name', StringType(), True), StructField('address', StringType(), True), StructField('nationkey', LongType(), True), StructField('phone', StringType(), True), StructField('acctbal', DoubleType(), True), StructField('mktsegment', StringType(), True), StructField('comment', StringType(), True)])
```

```
>>> customer_df.show(2)
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+
|custkey|              name|             address|nationkey|          phone|acctbal|mktsegment|             comment|
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+
|    751|Customer#000000751|e OSrreG6sx7l1t3w...|        0|10-658-550-2257|2130.98| FURNITURE|ges sleep furious...|
|    752|Customer#000000752|KtdEacPUecPdPLt99...|        8|18-924-993-6038|8363.66| MACHINERY|mong the ironic, ...|
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+
only showing top 2 rows
```

## Simple data operations/transformations with PySpark
Show unique values in the "mktsegment" column.

```
>>> customer_df.select('mktsegment').distinct().show()
+----------+
|mktsegment|
+----------+
| FURNITURE|
| MACHINERY|
| HOUSEHOLD|
|  BUILDING|
|AUTOMOBILE|
+----------+
```

Create new dataframe with data specific to "FURNITURE" market segment.
```
>>> customer_df.filter(customer_df.mktsegment == "FURNITURE").show(2)
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+
|custkey|              name|             address|nationkey|          phone|acctbal|mktsegment|             comment|
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+
|    751|Customer#000000751|e OSrreG6sx7l1t3w...|        0|10-658-550-2257|2130.98| FURNITURE|ges sleep furious...|
|    759|Customer#000000759|IX1uj4NFhOmu0V xD...|        1|11-731-806-1019|3477.59| FURNITURE|above the quickly...|
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+
only showing top 2 rows
```
Simple join of 2 tables

```
>>> customer_df=spark.read.table("lakehouse.example_03.customer")
>>> orders_df=spark.sql("select * from example_03.orders")
>>> joined_customer_orders_df=customer_df.join(orders_df, customer_df.custkey == orders_df.custkey)
>>> joined_customer_orders_df.show(2)
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+--------+-------+-----------+----------+----------+---------------+---------------+------------+--------------------+
|custkey|              name|             address|nationkey|          phone|acctbal|mktsegment|             comment|orderkey|custkey|orderstatus|totalprice| orderdate|  orderpriority|          clerk|shippriority|             comment|
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+--------+-------+-----------+----------+----------+---------------+---------------+------------+--------------------+
|    848|Customer#000000848|    a nIm5Bk7 RMqMZ6|       15|25-655-714-7125|5685.59|  BUILDING|st furiously blit...|   49989|    848|          F|  36980.39|1993-04-27|4-NOT SPECIFIED|Clerk#000000450|           0|e slyly among the...|
|    625|Customer#000000625|uvgDE6eQ2bJp4BkHy...|       13|23-789-801-2873|5744.89| FURNITURE|, pending deposit...|   49990|    625|          F|  12270.89|1994-09-06|4-NOT SPECIFIED|Clerk#000000835|           0| slyly regular pa...|
+-------+------------------+--------------------+---------+---------------+-------+----------+--------------------+--------+-------+-----------+----------+----------+---------------+---------------+------------+--------------------+
only showing top 2 rows

```
## Frequence Pattern Growth - Data Mining
Given a dataset of transactions, the first step of FP-growth is to calculate item frequencies and identify frequent items. FP Growth is an algorithm that helps find association rules.

```
>>> from pyspark.ml.fpm import FPGrowth
>>> from pyspark.sql.functions import split, col
>>> order_basket=spark.read.options(inferSchema='True',delimiter=',', header=True).csv("/Users/drangar/Development/watsonx-data-public/tx3509-labs/data/ORDERBASKET.csv")
>>> order_basket_array=order_basket.select(col("id"),split(col("items"),",").alias("items"))
>>> fpGrowth = FPGrowth(itemsCol="items", minSupport=0.5, minConfidence=0.6)
>>> association_model= fpGrowth.fit(order_basket_array)

```
```

>>> association_model.associationRules.show()
+--------------+--------------+------------------+------------------+-------+
|    antecedent|    consequent|        confidence|              lift|support|
+--------------+--------------+------------------+------------------+-------+
|[Womens top 6]|[Mens shirt 1]|               1.0|1.3333333333333333|    0.5|
|[Mens shirt 1]|[Womens top 6]|0.6666666666666666|1.3333333333333333|    0.5|
|[Mens shirt 1]|[Mens pants 3]|0.6666666666666666|0.8888888888888888|    0.5|
|[Mens pants 3]|[Mens shirt 1]|0.6666666666666666|0.8888888888888888|    0.5|
+--------------+--------------+------------------+------------------+-------+

```

## Writing to the IBM Lakehouse
Writing to the IBM lakehouse using Apache Spark is very simple, we just need to use the write method of the Spark dataframe and provide the schema and table name to save it as.

```
>>> association_model.associationRules.write.saveAsTable("lakehouse.example_03.association_rules")
>>> spark.read.table("lakehouse.example_03.association_rules").show()
+--------------+--------------+------------------+------------------+-------+
|    antecedent|    consequent|        confidence|              lift|support|
+--------------+--------------+------------------+------------------+-------+
|[Womens top 6]|[Mens shirt 1]|               1.0|1.3333333333333333|    0.5|
|[Mens shirt 1]|[Womens top 6]|0.6666666666666666|1.3333333333333333|    0.5|
|[Mens shirt 1]|[Mens pants 3]|0.6666666666666666|0.8888888888888888|    0.5|
|[Mens pants 3]|[Mens shirt 1]|0.6666666666666666|0.8888888888888888|    0.5|
+--------------+--------------+------------------+------------------+-------+

```