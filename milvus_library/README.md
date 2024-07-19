# milvus_library
The package package will be used for integration with other services and applications

# Design

1. User input specifies the environment in use (e.g. saas or on-prem)
2. The user input is saved in the config.properties file against the parameter "Platform"
3. The python code consumes the platform value and executes the corresponding code to identify Milvus presence.
4. If a service exists, the "getEngineDetails" function retrieves all the service details (e.g. grpc/rest urls, service id, state, etc.) and stores.
5. The stored values are consumed to establish connection to the said service using "connection" function.
6. A sample similarity search code is executed to validate the connection.
7. "milvusRunner" executes all steps in a sequential order per the platform details.
8. "utils.py" includes the session token that is generated dynamically to access the service details and the instance.

Note: We could leverage the RAG based similarity search code in place of the sample code once the design looks good. 
