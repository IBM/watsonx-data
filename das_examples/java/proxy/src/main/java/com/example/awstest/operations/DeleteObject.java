package com.example.awstest.operations;

import com.amazonaws.AmazonServiceException;
import com.amazonaws.services.s3.AmazonS3;

public class DeleteObject {
     public static void deleteObjectTest(AmazonS3 s3, String bucket_name, String object_key) {
        System.out.format("Deleting object %s from S3 bucket: %s\n", object_key,
                bucket_name);
        try {
            s3.deleteObject(bucket_name, object_key);
        } catch (AmazonServiceException e) {
            System.err.println(e.getErrorMessage());
            System.exit(1);
        }
        System.out.println("Done!");
    }
}
