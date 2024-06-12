## IBM watsonx.data
IBM® watsonx.data is a new open architecture lakehouse that combines the open, flexible, and low-cost storage benefits of data lakes with the transactional qualities and performance of the data warehouse. The best-in-class features and optimizations available in watsonx.data make it an optimal choice for next generation data analytics and automation. It offers a single platform where you can attach data residing in object store and relational databases, synthesize the data through a SQL interface and make the data available for AI and BI applications. To learn more, see [watsonx.data](https://www.ibm.com/products/watsonx-data)


## IBM watsonx.data developer version
The watsonx.data developer version is an entry-level watsonx.data for the student, developer and partner community. The developer version offers a set of containers that can be installed on a suitable host machine at the same release level as the Enterprise version, with restricted features. For more information see [watsonx.data developer version](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=edition-installing-watsonxdata-developer-version)

## Installing watsonx.data developer version
To install watsonx.data developer version, you will need the ibm-lh-dev.tgz and the container images.

### Before you begin
1. You need to procure credentials to access the container images for the developer version hosted in the IBM container registry. <br>
   If you have purchased watsonx.data, you can use your entitlement key from [My IBM](https://myibm.ibm.com/products-services/containerlibrary?_gl=1%2a1o6moo1%2a_ga%2aMTgxNzQxMzQ4OS4xNjk0NTg0Nzky%2a_ga_FYECCCS21D%2aMTY5NDY1NzI0Ny43LjEuMTY5NDY1NzcxMC4wLjAuMA..). If you have not purchased watsonx.data, reach out to your IBM contact to get the read key to access the watsonx.data images. Depending on how the entitlement key was generated, you will need to specify the users as either `iamapikey` or `cp`.
3. Setup a single-node virtual machine to install the package. The supported operating system environments are
- Linux
- Windows
- Mac OS x86
- Mac with Apple Silicon with Rosetta. For more information see [here](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=version-prerequisites-watsonxdata-installation-mac)
4. Install `docker` or `podman` on the machine to run the container images.
<br>If you are using SUSE Linux, `podman` is only availaible for version SLES 15.4. Also, make sure to upgrade the system first (`zypper dist-upgrade`) before installing the dependencies that are not provided but are needed for the installation of `docker` or `podman`. 

For Docker:
- `sysuser-shadow` in SLES 12.5
- `catatonit` in SLES 15.5

For Podman:
- `fuse-overlayfs` in SLES 15.4

Packages can be downloaded from the [official site](https://software.opensuse.org/package/).

5. Install `podman-plugins`. It is important that you install `podman-plugins` before intalling watsonx.data.
```
yum install podman-plugins
```
For SUSE, install [cni-plugin-dnsname](https://build.opensuse.org/package/show/home:ojkastl_buildservice:docker_compose_etc/cni-plugin-dnsname) instead.

### Procedure
1. Set up the installation directory and environment variables

a. Create a directory under which you wish to install watsonx.data developer version.
   ```
   export LH_ROOT_DIR=~/ibm-watsonx-data
   mkdir $LH_ROOT_DIR
   cd $LH_ROOT_DIR
   ```
b. Download and extract the developer package<br>
   ```
   wget https://github.com/IBM/watsonx-data/releases/download/v1.1.4/ibm-lh-dev-1.1.4-120-20240410-200742-onprem-v1.1.4.tgz
   ```  
   ```
   tar -xvf ibm-lh-dev-1.1.4-120-20240410-200742-onprem-v1.1.4.tgz
   ```
   This will create a directory by the name `ibm-lh-dev`

c. Review the license files located under `$LH_ROOT_DIR/ibm-lh-dev/licenses`

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
4. Optional: You can customize your installation by editting the values in `$LH_ROOT_DIR/ibm-lh-dev/etc/launch_config.env`
5. Run the setup script
   ```
   ./ibm-lh-dev/bin/setup --license_acceptance=y --runtime=docker
   ```
   or
   ```
   ./ibm-lh-dev/bin/setup --license_acceptance=y --runtime=podman
   ```
   This will pull the images from the container registry and perform the initial setup.

## Managing the developer version
The developer version includes a convenient set of scripts that allow you to manage the installation

### Starting watsonx.data
To start all the containers, run the following command
```
$LH_ROOT_DIR/ibm-lh-dev/bin/start
```

### View the status of watsonx.data
To check the status of all the containers, run the following command
```
$LH_ROOT_DIR/ibm-lh-dev/bin/status --all
```

### Stop watsonx.data
To stop all the containers, run the following command
```
$LH_ROOT_DIR/ibm-lh-dev/bin/stop
```

### User management
When you run the `setup` command to install the developer version, it will create a default user `ibmlhadmin` with password `password`. This user has admin privileges on teh installation.
You can a users by running the following command
```
./ibm-lh-dev/bin/user-mgmt add-user <user-name> Admin|User <user-password>
```
You can delete a user by running ths following command
```
./ibm-lh-dev/bin/user-mgmt delete-user <user-name>
```


## Working with watsonx.data

### UI Interface
You can access the UI interface by visitng https://localhost:9443, or https:/<machine_name>:9443 if you have installed on a remote machine.
To login, specify `ibmlhadmin` for the Username field and `password` for the Password field. These are the default values. If you have customized the install, you will need to specify the values accordingly.

### API interface
You can interact with watsonx.data through the API interface. For more details, see https://cloud.ibm.com/apidocs/watsonxdata-software

### presto-cli interface
The developer version includes `presto-cli` to allow you to directly interact with presto. You can run `presto-cli` if you want to access presto in an interactive mode, and run `presto-run` to access in non-interactive mode.
You will be accessing presto as user `ibmlhadmin`. If you want to interact as any other user added to the installation, use the client package.


## Examples
The developer version includes examples that can be used to explore the product and build further use cases.
The examples are located under `$LH_ROOT_DIR/ibm-lh-dev/examples`
