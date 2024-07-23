# How to use non-ibm spark to work with watsonx.data
First follow below step install spark and download the relative jar files.

## !!! Must use ibm provide hive jars, using opensource one will failed to connect hive-metastore in watsonx.data
https://developer.ibm.com/tutorials/awb-test-data-ingestion-to-watsonx-data/

In above doc ,missing iceberg-spark-runtime, if using icebergsparksessionextension
```
.config("spark.sql.extensions","org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
```
Pls download iceberg-spark-runtime and also put in your <spark install directory>/jars/, you can run below command to get spark install directory
```
  brew info apache-spark
```
```
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.12/1.4.0/iceberg-spark-runtime-3.4_2.12-1.4.0.jar
```

If testing using signature, you also need add custom-credential-provider into <spark install dir>/jars/

Then you can look the python script
