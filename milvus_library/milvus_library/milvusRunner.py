import milvus_library.getEngineDetails as getEngineDetails, milvus_library.getInstanceDetails as getInstanceDetails, milvus_library.connection as connection, configparser
import milvus_library.getConfigProperties as properties
import warnings
import pkg_resources
file_path = pkg_resources.resource_filename("milvus_library", "config.properties")
def main():
    properties.getConfigProperties(file_path)
    config=configparser.ConfigParser()
    config.read(file_path)
    platform = config.get('GENERAL','platform')

    if (platform == 'cpd'):
        getInstanceDetails.get_instance_id()
        getEngineDetails.getEngineDetails(file_path=file_path)
        connection.setup_milvus_connection()

    elif (platform == 'saas'):
        getEngineDetails.getEngineDetails(file_path=file_path)
        connection.setup_milvus_connection()
    
    warnings.filterwarnings("ignore")
    