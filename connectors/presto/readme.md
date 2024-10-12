# IBM created Presto connectors that may be useful to you

## Snowflake connector

### Overview

Snowflake is a cloud-based data platform that allows users to store, analyze, and share data.

The Snowflake connector allows querying and creating tables in an external
Snowflake database. This can be used to join data between different
systems like Snowflake and Hive, or between two different Snowflake accounts.

### Connector Configuration

To configure the Snowflake connector, create a catalog properties file in *etc/catalog* named, for example, *snowflake.properties*, to mount the Snowflake connector as the snowflake catalog. Create the file with the following contents, replacing the connection properties as appropriate for your setup:

```
connector.name=snowflake
connection-url=jdbc:snowflake://<account_identifier>.snowflakecomputing.com/?db={dbname}  
connection-user={username}
connection-password={password}
```

The `connection-url` defines the connection information and parameters to pass to the Snowflake JDBC driver.

Syntax: `jdbc:snowflake://<account_identifier>.snowflakecomputing.com/?<connection_params>`

User has to provide only the `account_identifier`, and shouldn't include the prefix `.snowflakecomputing.com`

The `connection-user` and `connection-password` are typically required and determine the user credentials for the connection.

### SSL Configuration

By default, connections to Snowflake use SSL.

### Integrating the Snowflake Plugin to Presto

1. Clone the repository [watsonx-data](https://github.com/IBM/watsonx-data).

2. Navigate to the folder *watsonx-data/connectors/presto/presto-snowflake*.

3. Run the following command to build the module:

    `mvn clean install -DskipTests`

4. Rename the directory *`presto-snowflake-<VERSION>-SNAPSHOT`* generated within the target folder, which holds the essential JARs, using the below command:

    `mv presto-snowflake-<version>-SNAPSHOT snowflake`

5. Place the folder within the plugins directory, located at *`presto-server-<VERSION>/plugin`*.  

6. Create the file `snowflake.properties` at the following path `etc/catalog/snowflake.properties`, replacing the properties as appropriate.

7. Append the property `allow-drop-table` to `true` in `etc/catalog/snowflake.properties` to allow dropping Snowflake tables from Presto via `DROP TABLE` (defaults to `false`).

8. Run the Presto server:

    `bin/launcher start`


### Multiple Snowflake Databases or Accounts

The Snowflake connector can only access a single database within
a Snowflake account. Thus, if you have multiple Snowflake databases,
or want to connect to multiple Snowflake accounts, you must configure
multiple catalog entries of the Snowflake connector.

To add another catalog, simply add another properties file to ``etc/catalog``
with a different name, making sure it ends in ``.properties``. For example,
if you name the property file ``sales.properties``, Presto creates a
catalog named ``sales`` using the configured connector.

### Querying Snowflake

The Snowflake connector provides a schema for every Snowflake *database*.
You can see the available Snowflake schemas by running ``SHOW SCHEMAS``::

    SHOW SCHEMAS FROM snowflake;

If you have a Snowflake schema named ``web``, you can view the tables
in this schema by running ``SHOW TABLES``::

    SHOW TABLES FROM snowflake.web;

You can see a list of the columns in the ``clicks`` table in the ``web`` schema
using either of the following::

    DESCRIBE snowflake.web.clicks;
    SHOW COLUMNS FROM snowflake.web.clicks;

You can access the ``clicks`` table in the ``web`` schema::

    SELECT * FROM snowflake.web.clicks;

If you used a different name for your catalog properties file, use
that catalog name instead of ``snowflake`` in the above examples.

### Snowflake Connector Limitations

The following SQL statements are not supported:

- [CREATE SCHEMA](https://prestodb.io/docs/0.286/sql/create-schema.html) 
- [ALTER SCHEMA](https://prestodb.io/docs/0.286/sql/alter-schema.html)
- [GRANT](https://prestodb.io/docs/0.286/sql/grant.html)
- [REVOKE](https://prestodb.io/docs/0.286/sql/revoke.html)
- [SHOW ROLES](https://prestodb.io/docs/0.286/sql/show-roles.html)
- [SHOW ROLE GRANTS](https://prestodb.io/docs/0.286/sql/show-role-grants.html)
- [CREATE ROLE](https://prestodb.io/docs/0.286/sql/create-role.html)
- [CREATE VIEW](https://prestodb.io/docs/0.286/sql/create-view.html)
- [DROP SCHEMA](https://prestodb.io/docs/0.286/sql/drop-schema.html)
- [DROP VIEW](https://prestodb.io/docs/0.286/sql/drop-view.html)
- [TRUNCATE](https://prestodb.io/docs/0.286/sql/truncate.html)
- [UPDATE](https://prestodb.io/docs/0.286/sql/update.html)
- [DELETE](https://prestodb.io/docs/0.286/sql/delete.html)

### Running the unit testcases in **presto-snowflake** module

Run the following command from the *presto* root directory to run the unit testcases in the *presto-snowflake* module:

```
mvn test -pl presto-snowflake -Dsnowflake.test.server.url=jdbc:snowflake://<account_identifier>.snowflakecomputing.com/ -Dsnowflake.test.server.user={username} -Dsnowflake.test.server.password={password} -Dsnowflake.test.server.database={dbname} -Dsnowflake.test.server.warehouse={warehousename} -Dsnowflake.test.server.role={role} -Dsnowflake.test.server.schema={schema}
```


