# A Tour of the `ibm-lh-client` utilities

The `ibm-lh-client` package provides a set of utilities that will help you connect to a watsonx.data instance. For example, `presto-cli` helps you connect to a remote watsonx.data Presto engine, `python-run`` helps you run python applications against watsonx.data. These utilities run inside containers that include all the basic software packages needed to provide a well-defined environment needed to connect to a remote watsonx.data instance. 

In this section, we will take a quick look at some of the utilities in the client package and connect to the "local" watsonx.data Developer installation.

## Exercise 13-1.  Add connection information for a Presto engine 

In this exercise, you will add the Presto engine installed and started from  `ibm-lh-dev` on the same VM.

a) Find the hostname to use (other than localhost)

If `hostname` returns `localhost.localdomain`, it means the VM does not has a hostname set.

If the VM does not have a hostname assigned and because TLS certificate signing requires a hostname, workaround by setting specific host ames.

- add: 
`ibm-lh-presto-svc` and `lhconsole-api-svc` to the 127.0.0.1 entry in `/etc/hosts`

for example:

```
127.0.0.1 localhost ibm-lh-presto-svc lhconsole-api-svc
```

b) Trust self-signed certificates 

  The `bin/cert-mgmt`` utility adds CA certificates served by watsonx.data installation to its trust store(for usage, run cert-mgmt --help). This is useful when self-signed certificates are being served, such as with Software installations.

  (use the assigned hostname for the VM or if not, `ibm-lh-presto-svc` )

  ```
  ibm-lh-client/bin/cert-mgmt --op=add --host=ibm-lh-presto-svc --port=8443
  ```

c) Use bin/manage-engines to register the Presto engine.

   We will use the name `wxd` to identify this Presto server.

   ```
   ibm-lh-client/bin/manage-engines --op=add --name=wxd --host=ibm-lh-presto-svc --port=8443 --username=ibmlhadmin
   ```

  enter the password for the `ibmlhadmin` user when prompted.

d) Verify

   ```
   ibm-lh-client/bin/manage-engines --op=list
   ```

  and

  ```
  ibm-lh-client/bin/manage-engines --op=details --name=wxd
  ```

You can connect to multiple Presto servers in this fashion.  You will then refer to each by using the name with the `--engine=` argument. The addition of the engine included the credentials to be used, hence the utilities would not prompt you each time.

## Exercise 13-2a.  Query with presto-run

for example:

```
ibm-lh-client/bin/presto-run --engine=wxd --catalog=tpch --execute 'select * from tiny.customer limit 10'
```

For reference:  https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=client-running-sql-queries-by-using-lh

## Exercise 13-2b. Start a presto-cli session

for example:

```
ibm-lh-client/bin/presto-cli --engine=wxd --catalog=tpch
presto> select * from tiny.customer limit 10;
```

**Note** the `ibm-lh-dev` Developer edition installation includes a `presto-run` as well which behaves in an identical fashion. The key difference is that the `ibm-lh-dev` version automatically connects to its own Presto server (there is no `--engine=` argument), while `ibm-lh-client` is meant to work with many watsonx.data instances and multiple Presto servers.


## Exercise 13-3. Using the ibm-lh utility

The ibm-lh utility invokes the watsonx.data REST API. In this exercise, you will try out some of these options.

Reference: https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=package-setting-up-lh-cli-utility


a) Trust the API server's self-signed certificates 

  The `bin/cert-mgmt`` utility adds CA certificates served by watsonx.data installation to its trust store(for usage, run cert-mgmt --help). This is useful when self-signed certificates are being served, such as with Software installations.

  (use the assigned hostname/port for the VM or the remote wxd Service you are connecting to or  `lhconsole-api-svc, 3333` )

 for example:

  ```
  ibm-lh-client/bin/cert-mgmt --op=add --host=lhconsole-api-svc --port=3333
  ```

b) Connect to the wxd API Server 

```
ibm-lh-client/bin/connect-lh --op=add  --name=wxd-api  --host=lhconsole-api-svc  --port=3333  --username=ibmlhadmin
```

enter the password for the `ibmlhadmin` user when prompted.

To verify `ibm-lh-client/bin/connect-lh --op=list`


c)  Select the dev wxd config

`ibm-lh-client/bin/ibm-lh config add_dev --name wxd-api  --host=lhconsole-api-svc  --port=3333`


You can then try out some of the commands described here: https://www.ibm.com/docs/en/watsonxdata/1.0.x?topic=utility-lh-commands-usage#ibm_lh_commands__engine

d) Get a list of engines on that wxd installation

`ibm-lh-client/bin/ibm-lh engine ls`

e) Get a list of buckets 

`ibm-lh-client/bin/ibm-lh bucket ls`
