import getEngineDetails, getInstanceDetails, connection, configparser, similaritySearch

def main():

    config=configparser.ConfigParser()
    config.read('config.properties')
    platform = config.get('GENERAL','platform')

    if (platform == 'cpd'):

        getInstanceDetails.get_instance_id()
        getEngineDetails.getEngineDetails()
        connection.setup_milvus_connection()
        similaritySearch.similarity_search()

    elif (platform == 'saas'):

        getEngineDetails.getEngineDetails()
        connection.setup_milvus_connection()
        similaritySearch.similarity_search()