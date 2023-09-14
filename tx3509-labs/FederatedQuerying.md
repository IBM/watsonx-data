
# Federated Querying

In this exercise, we will join data from a PostgreSQL database with iceberg tables in the `retail` schema. 

The Developer edition deploys an containerized version of PostgreSQL which we will reuse for this exercise. Note you can choose to add a database that is network accessible to the wxd installation.  In subsequent releases, you will see more "Connectors" supported for a broader variety of data source types.

## Setup PostgreSQL demo database

**Exercise 10a):** create PostgresSQL table and load data

1) copy a sample csv to the sandbox directory.

`cp data/CUSTOMER.csv  $LH_SANDBOX_DIR/.`


2). We will create a sample table and load some data into the `postgres` database. You can use a convenient shell script inside the dev-sandbox.


You can do this with the dev-sandbox.  Note - if you are using your own database, you can do something similar with the `psql` utility or something like DBeaver.

```
bin/dev-sandbox /scripts/runsql.sh postgres
```

You will see an interactive `postgres=#` prompt.

3) Create a schema & table in PostgreSQL

```
create schema IF NOT EXISTS mart;
CREATE TABLE IF NOT EXISTS mart.customer (
   "custkey" integer,
   "name" varchar,
   "address" varchar,
   "nation" varchar,
   "phone" varchar,
   "acctbal" real,
   "mktsegment" varchar,
   "comment" varchar
);

```

4) load table from the sandbox location

```
\copy mart.customer from /tmp/sbox/CUSTOMER.csv delimiter ',' csv header;
```

`COPY 1000` in the response will indicate that a 1000 rows were loaded.

to confirm:

`select * from mart.customer limit 10;`

` \q`  to exit the PostgreSQL prompt

6). In your lab environment's terminal, get the generated password for the postgreSQL instance.

`docker exec -it ibm-lh-postgres env | grep POSTGRES_PASSWORD`

If you are using your own database, make sure to get credentials ready for use with wxd.

---

## Add the PostgreSQL database to wxd

**Exercise 10b):** Add a 'mart' catalog to wxd 

You can do this via the "Add component -> Database" in the wxd Infrastructure user experience.

For example, see this recording

<img src="./images/add-postgres-martdb-to-lh.gif">


**Exercise 10c):** Access the data in the mart catalog using Presto

```
bin/presto-run --catalog=mart --execute='select * from mart.customer limit 10'
```

---

## Create a join with tables in iceberg and presto


**Exercise 10c):**  Write a query to find the orders for all the customers in the newly created postgreSQL table

This would involve a join with the `orders` table and this `customer` table - across two catalogs

---

- return back to the [Main lab exercises](./README.md)
 

