
## Config DAS
1. Get DAS endpoint from Information Window(the i icon in the left menu)
2. Download DAS cert
```
echo QUIT | openssl s_client -showcerts -connect <cas host>:443 | awk '/-----BEGIN CERTIFICATE-----/ {p=1}; p; /-----END CERTIFICATE-----/ {p=0}' > das.cert
```

Then using keytool to import the cert to your local truststore

```
sudo keytool -import -trustcacerts -cacerts -storepass changeit -noprompt -alias das-cert -file ./das.cert
```
Attention: You may need restart your runtime to reload the cacert.


# How to use non-ibm spark to work with watsonx.data
First follow below step install spark and download the relative jar files.

## !!! Must use ibm provide hive jars, using opensource one will failed to connect hive-metastore in watsonx.data
https://developer.ibm.com/tutorials/awb-test-data-ingestion-to-watsonx-data/

## Add iceberg runtime if using iceberg

```
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.12/1.4.0/iceberg-spark-runtime-3.4_2.12-1.4.0.jar
```


## If you using sparksql, pls also Config HMS
1. Expose HMS port
https://www.ibm.com/docs/en/watsonx/watsonxdata/2.0.x?topic=administering-accessing-hive-metastore-hms-using-nodeport
2. Get HMS endpoint from Infrastructure Manager/<your catalog> 
3. Download Cert follow below guide
https://www.ibm.com/docs/en/watsonx/watsonxdata/2.0.x?topic=administering-importing-hms-self-signed-certificates-java-truststore


## if using icebergsparksessionextension, pls config iceberg
```
.config("spark.sql.extensions","org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
```

## For the download jars you can add in spark configure or direct add the spark/jars folder
Pls download iceberg-spark-runtime and also put in your <spark install directory>/jars/, you can run below command to get spark install directory
```
  brew info apache-spark
```

