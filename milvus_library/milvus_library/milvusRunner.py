import pkg_resources
import milvus_library.getEngineDetails as getEngineDetails, milvus_library.getInstanceDetails as getInstanceDetails, configparser, milvus_library.milvusConnect as milvusConnect
#import milvus_library.connection as connection,

def main(crn, database, service_name, connection_type, platform):

    file_path = pkg_resources.resource_filename("milvus_library", "config.properties")


    config=configparser.ConfigParser()
    config.read('config.properties')
    #platform = config.get('GENERAL','platform')

    config.set("SAAS", "crn", crn)
    config.set("GENERAL", "platform", platform)
    config.set("GENERAL", "database", database)
    config.set("GENERAL", "service_name", service_name)
    config.set("GENERAL", "connection_type", connection_type)

    with open('config.properties', 'w') as configfile:
                config.write(configfile)

    if (platform == 'cpd'):

        getInstanceDetails.get_instance_id()
        getEngineDetails.getEngineDetails()
        milvusConnect.setup_milvus_client_connection()
        #connection.setup_milvus_connection()
        # similaritySearch.similarity_search()

    elif (platform == 'saas'):

        getEngineDetails.getEngineDetails(file_path)
        #connection.setup_milvus_connection()

        if (connection_type == "milvusclient"):
            milvus_client = milvusConnect.setup_milvus_client_connection()
            return milvus_client
        elif (connection_type == "orm"):
            milvusConnect.setup_milvus_orm_connection()  
        

    
