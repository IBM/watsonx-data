#  View the physical data organization in the Object store bucket

Now that we have loaded some data into the `iceberg_data` catalog, we will look at how the data is physically stored in iceberg tables.

We will look at the buckets hosted by the Minio S3 server in this environment.  You will need to export the minio UI port and get the (generated credentials to use)

- open up the minio port

```
ibm-lh-dev/bin/expose-minio
``` 

you will see an output such as this:

 ```
FYI: LH_RUN_MODE is set to diag
019b4a8bd1661e220221bd013e3f6abf5682145c3fd46266e5d41b8696f7f028
Minio credentials:
    username: e18a57a138df8f9c33d1645a
    password: a9644d59a0b9fe6de72b5f3d
Ports:
    S3 endpoint port: 9000
    Minio console port: 9001 
 ```

- access the minio console 

visit https://localhost:9001 from your browser

Enter the credentials from the `expose-minio`` output

- Navigate to the customer table
 
 metadata:  iceberg-bucket/retail/customer/metadata

 data: iceberg-bucket/retail/customer/data

- use `ibm-lh-dev/examples/03-iceberg-table.sh` 

  and describe the parquet customer data file.

---
