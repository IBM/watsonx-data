## dbt-watsonx-presto

### Project description
[dbt](https://www.getdbt.com/) enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications.

dbt is the T in ELT. Organize, cleanse, denormalize, filter, rename, and pre-aggregate the raw data in your warehouse so that it's ready for analysis.

### dbt-watsonx-presto
The `dbt-watsonx-presto` is a dbt adapter designed to connect dbt Core with Presto, specifically for use with IBM watsonX.data (wxd) Presto clusters. This adapter supports both wxd on-prem and saas, enabling you to build, test, and document data models in wxd Presto.

Read the official documentation for using watsonx.data with dbt-watsonx-spark -

- Documetnation for IBM Cloud and SaaS offerrings
- Documentation for IBM watsonx.data software

### Getting started

- [Install dbt](https://docs.getdbt.com/docs/core/installation-overview)
- Read the [introduction](https://docs.getdbt.com/docs/introduction) and [viewpoint](https://docs.getdbt.com/community/resources/viewpoint)

### Installation
To install the `dbt-watsonx-presto` plugin, use pip:
```
$ pip install dbt-watsonx-presto
```

### Configuration
#### Setting Up Your Profile

To connect dbt Core to your wxd Presto clusters, configure the `profiles.yml` file located in the `.dbt/` directory of your home directory. Below is an example configuration for both `on-prem` and `SaaS`:

**Example profiles.yml entry:**
```
my_project:
  outputs:
    on-prem:
      type: presto
      method: BasicAuth
      user: username
      password: password
      host: internal/external host
      port: 443
      database: analytics
      schema: dbt_drew
      threads: 8
      ssl_verify: path/to/certificate
      
    saas:
      type: presto
      method: BasicAuth
      user: username
      password: api_key
      host: 127.0.0.1
      port: 8080
      database: analytics
      schema: dbt_drew
      threads: 8
      ssl_verify: true
      
  target: on-prem
```
#### Configuration Options

| **Option**       | **Description**                                                                                                 | **Required?**               | **Example**                  |
|--------------|-------------------------------------------------------------------------------------------------------------|-------------------------|--------------------------|
| method       | Authentication method for wxd Presto                                                        | Optional (default is `none`)  | `none` or `BasicAuth` |
| user         | Username for authentication                                                                                 | Required  | `drew` |
| password     | Password or API key for authentication                                                                          | Required if `method` is `BasicAuth`  | `none` or `abc123` |
| http_headers | HTTP Headers to send alongside requests to Presto, specified as a yaml dictionary of (header, value) pairs. | Optional |  `X-Presto-Routing-Group: my-cluster`|
| http_scheme  | HTTP scheme to use (`http` or `https`)                                                               | Optional (default is `http`, or `https` for `method: BasicAuth`) | `https` or `http`
| database     | catalog name for building models                                                               | Required  | `analytics` |
| schema       | schema for building models                                                                    | Required | `dbt_drew` |
| host         | Hostname for connecting to wxd Presto | Required | `127.0.0.1`  |
| port         | Port for connecting to wxd Presto (`443` for the external host of on-prem).                       | Required | `8080` |
| threads      | Number of threads for dbt operations                                                                             | Optional (default is `1`) | `8` |
| ssl_verify   | Path to the SSL certificate                                              | Optional (required for wxd `on-prem`) | `path/to/certificate` |

### Usage Notes

#### Supported Functionality
Due to the nature of wxd Presto, not all core dbt functionality is supported.
The following features of dbt are not implemented on wxd Presto:
- Archival
- Incremental models

#### Configuring Table Properties

When using wxd Presto, you can configure specific connector properties for dbt models via table properties

```
{{
  config(
    materialized='table',
    properties={
      "format": "'PARQUET'",
      "partitioning": "ARRAY['bucket(id, 2)']",
    }
  )
}}
```

### Basic dbt Commands

Here are some common dbt commands that you might use with `dbt-watsonx-presto`:

- **Initialize a dbt Project:** Set up a new dbt project.
```
dbt init my_project
```
- **Debug dbt Connection:** Test your dbt profile and connection.
```
dbt debug
```
- **Seed Data:** Load seed data into your database/datasource.
```
dbt seed
```
- **Run dbt Models:** Build and run your models.
```
dbt run
```
- **Test dbt Models:** Run tests on your models.
```
dbt test
```
- **Generate Documentation:** Create and serve documentation for your dbt project.
```
dbt docs generate
dbt docs serve
```

