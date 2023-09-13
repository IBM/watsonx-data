## IBM watsonx.data
IBM® watsonx.data is a new open architecture lakehouse that combines the open, flexible, and low-cost storage benefits of data lakes with the transactional qualities and performance of the data warehouse. The best-in-class features and optimizations available in watsonx.data make it an optimal choice for next generation data analytics and automation. It offers a single platform where you can attach data residing in object store and relational databases, synthesize the data through a SQL interface and make the data available for AI and BI applications.


## IBM watsonx.data developer package
The watsonx.data developer package is an entry-level version of watsonx.data for the student, developer and partner community. The developer version offers a set of containers that can be installed on a suitable host machine at the same release level as the Enterprise version, with restricted features.

## Installing watsonx.data developer package
To install watsonx.data developer package, you will need the ibm-lh-dev.tgz and the container images.

### Before you begin
1. Procure the read key to access the container images which are hosted in a IBM container registry. You can get the read key by signing up for the Academic Initiative (link to Academic Initiative portal), or the Partner program (link to Partner World portal)
2. Setup a single-node virtual machine to install the package. The supported operating system environments are
- Linux
- Windows
- Mac OS x86
- Mac with Apple Silicon with Rosetta. For more information see [here](https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=version-prerequisites-watsonxdata-installation-mac)
3. Install `docker` or `podman` on the machine to run the container images.
4. Install `podman-plugins`. It is important that you install `podman-plugins` before intalling watsonx.data.
```
yum install podman-plugins
```
5. Determine the version of watsonx.data that you want to install, and transfer respective the ibm-lh-dev-<version>.tgz from this github location to the machine, say to `/tmp`


### Procedure
1. Set up the installation directory and environment variables

a. Create a directory under which you wish to install watsonx.data developer package.
   ```
   export LH_ROOT_DIR=<install_directory>
   mkdir $LH_ROOT_DIR
   cd $LH_ROOT_DIR
   ```
b. Extract the developer package
   ```
   tar -xvf /tmp/ibm-lh-dev-<version>.tgz
   ```
   This will create a directory by the name `ibm-lh-dev`

c. Review the license files located under `$LH_ROOT_DIR/ibm-lh-dev/licenses`

2. Set the environment variables
   ```
   export LH_REGISTRY=icr.io/watsonx_data_dev_client_pkg
   ```

3. Authenticate to the container registry
   ```
   docker login $LH_REGISTRY -u iamapikey -p <read key procured from IBM>
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

## Managing the developer package
The developer package includes a convenient set of scripts that allow you to manage the installation

### Starting watsonx.data
To start all the containers, run the following command
```
$LH_ROOT_DIR/ibm-lh-dev/bin/start
```

### View the status of watsonx.data
To check the status of all the containers, run the following command
```
$LH_ROOT_DIR/ibm-lh-dev/bin/status
```

### Stop watsonx.data
To stop all the containers, run the following command
```
$LH_ROOT_DIR/ibm-lh-dev/bin/stop
```

### User management
When you run the `setup` command to install the developer package, it will create a default user `ibmlhadmin` with password `password`. This user has admin privileges on teh installation.
You can a users by running the following command
```
./ibm-lh-dev/bin/usermgmt add-user <user-name> Admin|User <user-password>
```
You can delete a user by running ths following command
```
./ibm-lh-dev/bin/usermgmt delete-user <user-name>
```


## Working with watsonx.data

### UI Interface
You can access the UI interface by visitng https:/<machine_name>:9443 as user `ibmlhadmin` with password `password`.
These are the default values. If you have cutomized the install, you will need to adjust them to match your customization.

### API interface
You can interact with watsonx.data through the API interface. For more details, see https://cloud.ibm.com/apidocs/watsonxdata-software

### presto-cli interface
The developer package includes `presto-cli` to allow you to directly interact with presto. You can run `presto-cli` if you want to access presto in an interactive moe, and run `presto-run` to access in non-interactive mode.
You will be accessing presto as user `ibmlhadmin`. If you want to interact as any other user added to the installation, use the client package.


## Examples
The developer package includes examples that can be used to explore the product and build further use cases.
The examples are located under `$LH_ROOT_DIR/ibm-lh-dev/examples`
