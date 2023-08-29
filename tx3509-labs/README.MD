

# Dive into the watsonx.data Lakehouse with the Developer Edition



TechXchange 2023 Hands on lab Session 3509:  https://reg.tools.ibm.com/flow/ibm/techxchange23/attendeeportal/page/sessioncatalog?search=3509


<CENTER>
<B>Coming soon</B>
</CENTER>

---

- [Dive into the watsonx.data Lakehouse with the Developer Edition](#dive-into-the-watsonxdata-lakehouse-with-the-developer-edition)
  - [Lab Setup](#lab-setup)
    - [Start all wxd containers](#start-all-wxd-containers)
    - [Check the status of all the containers](#check-the-status-of-all-the-containers)
    - [Explore the wxd Lakehouse](#explore-the-wxd-lakehouse)
  - [Organizing data: Catalogs, Schemas and Tables](#organizing-data-catalogs-schemas-and-tables)
    - [Exercise 1: List catalogs and schema](#exercise-1-list-catalogs-and-schema)
    - [Exercise 2: Select from a table](#exercise-2-select-from-a-table)
    - [Exercise 3: Create schema in the iceberg\_data Catalog](#exercise-3-create-schema-in-the-iceberg_data-catalog)
    - [Exercise 4: Create tables from csv files](#exercise-4-create-tables-from-csv-files)
    - [Exercise 5: View the physical data organization in the Object store bucket](#exercise-5-view-the-physical-data-organization-in-the-object-store-bucket)
  - [Querying for data with Presto](#querying-for-data-with-presto)
    - [Access Presto from Python](#access-presto-from-python)
      - [Using python-run](#using-python-run)
      - [Working with the developer sandbox container](#working-with-the-developer-sandbox-container)
  - [Federate external data](#federate-external-data)
    - [Setup PostgreSQL database](#setup-postgresql-database)
  - [Access Policies: Securing data](#access-policies-securing-data)
  - [Bringing data into your Lakehouse](#bringing-data-into-your-lakehouse)
  - [Analytics and ML with Spark](#analytics-and-ml-with-spark)
  - [Explore GraphQL for Data apps, powered by StepZen](#explore-graphql-for-data-apps-powered-by-stepzen)



---


## Lab Setup

The environment for the lab includes a slightly customized installation of the watsonx.data (wxd) Developer edition and a set of other utilities for you to explore and experiment with the Lakehouse.  This environment also includes minio based S3 buckets for storing data and a PostgreSQL instance that we will use as part of the federated querying exercise.

The credentials for the installation will be shared during the event.

### Start all wxd containers

`ibm-lh-dev/bin/start`

### Check the status of all the containers

```
ibm-lh-dev/bin/status --all
ibm-lh-hive-metastore                           running
ibm-lh-minio                            running
ibm-lh-postgres                         running                 5432/tcp
ibm-lh-presto                           running                 0.0.0.0:8443->8443/tcp
lhconsole-api                           running                 3333/tcp, 8081/tcp
lhconsole-javaapi-svc                           running                 8667/tcp
lhconsole-nodeclient-svc                                running                 3001/tcp
lhconsole-ui                            running                 0.0.0.0:9443->8443/tcp

```

### Explore the wxd Lakehouse

- To open the console UI, visit: https://localhost:9443 in your browser. 

    In the Infrastructure page you can see which buckets and catalogs are already present. 

    Use the Data Manager view to explore the catalogs and schema and the SQL view to run queries.

    The iceberg_data bucket and catalog is where we will load data into new tables and run queries. In the meantime, you can use the out of the box tpcds schema and explore 

    Note: this is a very small VM environment, so use only the "tiny" or "sf1" schema. The other schemas have larger datasets that you may not always be able to query.

    In the Data Manager view, expand on the left tree and select tables and view the table schema and sample data on the right.

    --insert pic---

    From the SQL Query Workspace, choose the tpcds tables and generate a SELECT staement 

    --insert pic---

- The Presto engine:

  The wxd installation includes one Presto engine container that serves as both the Coordinator and worker.  It is exposed on the host as port :8443
 
  The Presto Query monitoring UI is available via https://localhost:8443


- There is a convenient [DBeaver](https://dbeaver.io/) installation in the virtual machine.

  Launch DBeaver by clicking on the apps 

    --insert pic---

---

## Organizing data: Catalogs, Schemas and Tables 

While you can use the wxd browser based user experience to explore Catalogs and Schemas, in this section, we will look at using the command line.

### Exercise 1: List catalogs and schema

Explore the Lakehouse, using the presto-run utility

-   List all catalogs:

```
   ibm-lh-dev/bin/presto-run --execute 'show catalogs'
"hive_data"
"iceberg_data"
"jmx"
"system"
"tpcds"
"tpch"

```

- List all schemas in the tpcds catalog:

```

ibm-lh-dev/bin/presto-run --catalog tpcds --execute 'show schemas'
"information_schema"
"sf1"
"sf10"
"sf100"
"sf1000"
"sf10000"
"sf100000"
"sf300"
"sf3000"
"sf30000"
"tiny"

```

### Exercise 2: Select from a table 

- use the presto-run utility

```
  ibm-lh-dev/bin/presto-run --catalog tpcds --execute 'select * from "tpcds"."sf1"."catalog_page" limit 10'
```

- use presto CLI to run queries interactively

    `ibm-lh-dev/bin/presto-cli --catalog tpcds`

    and from the prompt, run a sample select

    ```
    presto> select * from tiny.customer_demographics limit 10;

    presto> quit;

    ```


### Exercise 3: Create schema in the iceberg_data Catalog

Note that creating a schema requires a location parameter to identify which path in the bucket to use for storing data

From the Data Manager UI, create a schema called 'retail',

--insert pic--

You can also create a schema from the cmd line

```

ibm-lh-dev/bin/presto-run --catalog iceberg_data --execute "CREATE SCHEMA IF NOT EXISTS retain with (location='s3a://iceberg-bucket/retail/')"

```


### Exercise 4: Create tables from csv files

To set up the next exercise we will create additional tables in the newly created `retail` schema and load them with sample data.


We will be creating 5 tables in the `retail` schema each from its own .csv file.

| Table name    | csv data  file |
| --------------| -------------- |
| customer      | CUSTOMER.csv   |
| orders        | ORDERS.csv     |
| nation        | NATION.csv     |
| lineitem      | LINEITEM.csv   |
| part          | PART.csv       |

For this purpose, we will use the Data Manager capability in the wxd UI.

--insert pics--


### Exercise 5: View the physical data organization in the Object store bucket

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

- Navigate to the retail path 

--insert-pic--

---


## Querying for data with Presto

### Access Presto from Python 

#### Using python-run

#### Working with the developer sandbox container

  The developer sandbox provides an environment with useful utilities and python modules to help explore the lakehouse
  To launch the sandbox 

   `bin/dev-sandbox`

## Federate external data

In this example, we will join data from a PostgreSQL database with iceberg tables in the `retail` schema.

### Setup PostgreSQL database

## Access Policies: Securing data

## Bringing data into your Lakehouse

## Analytics and ML with Spark

## Explore GraphQL for Data apps, powered by StepZen



