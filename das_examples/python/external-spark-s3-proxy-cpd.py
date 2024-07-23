from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StringType, StructType, IntegerType
#  watsonx.data access key
#CPD base64{<instanceid>|ZenAPIkey base64{username:<apikey>}}
#SaaS base64{<crn>|Basic base64{ibmlhapikey_<user_id>:<IAM_APIKEY>}}

# Current only support spark.hadoop.fs.s3a.path.style.access
spark = SparkSession.builder\
        .config("spark.hadoop.fs.s3a.endpoint", "<watsonx.data das endpoint>/cas/v1/proxy")\
        .config("spark.hadoop.fs.s3a.access.key","<watsonx.data access key>")\
        .config("spark.hadoop.fs.s3a.secret.key", "anystring")\
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")\
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.truststore.password","changeit") \
        .config("spark.hadoop.fs.s3a.truststore.path","/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/lib/security/cacerts") \
        .config("spark.hadoop.fs.s3a.truststore.type","JKS") \
        .getOrCreate()
conf = spark.sparkContext.getConf()
print(conf.getAll())

df =spark.read.text("s3a://lhbucket/proxytest/proxy-spark.txt")
df.show()
