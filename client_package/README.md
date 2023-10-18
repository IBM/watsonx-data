## IBM watsonx.data
IBM® watsonx.data is a new open architecture lakehouse that combines the open, flexible, and low-cost storage of data lakes with the transactional qualities and performance of the data warehouse. The best-in-class features and optimizations available on the watsonx.data make it an optimal choice for next generation data analytics and automation. It offers a single platform where you can attach data residing in object store and relational databases, synthesize the data through a SQL interface and make the data available for AI and BI applications. To learn more, see [watsonx.data](https://www.ibm.com/products/watsonx-data)


## IBM watsonx.data client package
The watsonx.data client package includes convenient utilities and pre-packaged libraries to access and develop applications that work with IBM watsonx.data. For more information see [watsonx.data client package](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=package-installing-lh-client)

## Installing watsonx.data client package
To install watsonx.data client package, you will need the ibm-lh-client.tgz and the container images.

### Before you begin
1. You need to procure credentials to access the container images for the client package hosted in the IBM container registry. 
    If you have purchased watsonx.data, you can use your entitlement key from [My IBM](https://myibm.ibm.com/products-services/containerlibrary?_gl=1%2a1o6moo1%2a_ga%2aMTgxNzQxMzQ4OS4xNjk0NTg0Nzky%2a_ga_FYECCCS21D%2aMTY5NDY1NzI0Ny43LjEuMTY5NDY1NzcxMC4wLjAuMA..). If you have not purchased watsonx.data, reach out to your IBM contact to get the read key to access the watsonx.data images. Depending on how the entitlement key was generated, you will need to specify the users as either `iamapikey` or `cp`.
2. Setup a single-node virtual machine to install the package. The supported operating system environments are
- Linux
- Windows
- Mac OS x86
- Mac with Apple Silicon with Rosetta. For more information see [here](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=version-prerequisites-watsonxdata-installation-mac)
3. Install `docker` or `podman` on the machine to run the container images. 
4. Install `podman-plugins`. It is important that you install `podman-plugins` before intalling watsonx.data.
```
yum install -y podman-plugins
```
5. Determine the version of watsonx.data that you want to install, and transfer respective the ibm-lh-client-<version>.tgz to the machine, say to `/tmp`


### Procedure
1. Set up the installation directory and environment variables

a. Set up a work directory. For example
   ```
   mkdir ~/ibm-watsonx-data
   cd  ~/ibm-watsonx-data
   ```
b. Download and extract the client package<br>
   ```
   wget https://github.com/IBM/watsonx-data/releases/download/v1.0.3/ibm-lh-client-1.0.3-255-20230912-165706-onprem-v1.0.3.tgz
   ``` 
   ```
   tar -xvf ibm-lh-client-1.0.3-255-20230912-165706-onprem-v1.0.3.tgz
   ```
   This will create a directory by the name `ibm-lh-client`
   
c. Review the license files located under `~/ibm-watsonx-data/ibm-lh-client/licenses`

2. Set the environment variables
   <br>If you have purchased watsonx.data, you should pull the container images from `cp.icr.io/cp/watsonx-data`
   ```
   export LH_REGISTRY=cp.icr.io/cp/watsonx-data
   ```
   If you have not purchased watsonx.data and have a readkey from IBM, you should pull the container images from `icr.io/watsonx_data_dev_client_pkg`
   ```
   export LH_REGISTRY=icr.io/watsonx_data_dev_client_pkg
   ```
3. Authenticate to the container registry
   ```
   docker login $LH_REGISTRY -u iamapikey -p <credentials>
   ```
   or
   ```
   podman login $LH_REGISTRY -u iamapikey -p <credentials>
   ```
4. Optional: You can customize your installation by editting the values in `~/ibm-watsonx-data/ibm-lh-client/etc/launch_config.env`
5. Run the setup script
   ```
   ./ibm-lh-client/bin/setup --license_acceptance=y --runtime=docker
   ```
   or
   ```
   ./ibm-lh-client/bin/setup --license_acceptance=y --runtime=podman
   ```
   This will pull the images from the container registry and start the container.


## Useful links
Refer to the following links for more information on using the client package<br>
[Commands and usage](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=utilities-lh-client-commands-usage) <br>
[Running SQL queries](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=utilities-running-sql-queries-by-using-lh-client) <br>
[Running Python scripts](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=utilities-running-python-scripts-by-using-lh-client)
