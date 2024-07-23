package com.example.awstest;

import java.io.IOException;

import com.amazonaws.SDKGlobalConfiguration;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.example.awstest.operations.DeleteObject;
import com.example.awstest.operations.GetObject;
import com.example.awstest.operations.ListObjects;
import com.example.awstest.operations.UploadObject;

public class AppUser1 {
    public static void main(String[] args) {
        
       //This example using non SSL, but you can reference guide how to connect with SSL.
        System.setProperty(SDKGlobalConfiguration.DISABLE_CERT_CHECKING_SYSTEM_PROPERTY, "true");

        String bucketName = "lhbucket";
        String keyName = "proxytest/c1.txt";

        String endpoint = "<DAS endpoint>/cas/v1/proxy";
      
        String secretKey = "any string";

        // Generate watsonx.data object storage access key follow below pattern
        // CPD base64{<instanceid>|ZenAPIkey base64{username:<apikey>}}
        // SaaS base64{<crn>|Basic base64{ibmlhapikey_<user_id>:<IAM_APIKEY>}}
        String accessKey ="<watsonx.data accesskey>";
       
        BasicAWSCredentials cos_cred = new BasicAWSCredentials(accessKey, secretKey);
        EndpointConfiguration cosEndPoint = new EndpointConfiguration(endpoint, "us-south");
        AmazonS3 s3Client = AmazonS3ClientBuilder.standard().withPathStyleAccessEnabled(true)
                .withCredentials(new AWSStaticCredentialsProvider(cos_cred))
                .withEndpointConfiguration(cosEndPoint).build();

       ListObjects.listObjectsTest(s3Client, bucketName);
       String dir=System.getProperty("user.dir");
       //Change to your local file name
       String fileName=dir+"/java/proxy/upload/post_test.txt";
       System.out.println("Upload file :"+fileName);

        try {
            UploadObject.uploadObjectTest(s3Client, bucketName, keyName,fileName);
        } catch (IOException e) {
            e.printStackTrace();
        }
        String downloadFile=dir+"/java/proxy/download/c1.txt";
        GetObject.GetObjectTest(s3Client, bucketName, keyName,downloadFile);

        DeleteObject.deleteObjectTest(s3Client, bucketName, keyName);

        GetObject.GetObjectTest(s3Client, bucketName, keyName,downloadFile);

    }

}
