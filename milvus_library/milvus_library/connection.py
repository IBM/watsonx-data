import configparser, requests, pkg_resources
from urllib.parse import urlparse
from pymilvus import connections
import warnings
warnings.filterwarnings("ignore")
fmt = "\n=== {:30} ===\n"
search_latency_fmt = "search latency = {:.4f}s"
file_path = pkg_resources.resource_filename("milvus_library", "config.properties")

def setup_milvus_connection():

    config=configparser.ConfigParser()
    config.read(file_path)
    platform = config.get('GENERAL','platform')
    url= config.get('MILVUS', 'milvus_grpc_url')
    parsed_url = urlparse(url)
    print(fmt.format("Estabilishing the Milvus connection"))
    if platform == "saas":
        connections.connect(

            secure=True,
            host = parsed_url.hostname,
            port = parsed_url.port,
            server_name = parsed_url.hostname,
            user=config.get('SAAS', 'saas_username'), 
            password=config.get('SAAS', 'password'),
            db_name=config.get('GENERAL', 'database')

            )
        
    elif platform == "cpd":

        connections.connect(
            secure=True,
            server_pem_path=config.get('CPD', 'cpd_cert_path'),
            server_name=config.get('MILVUS', 'milvus_grpc_url'),
            host=config.get('MILVUS', 'milvus_grpc_url'),
            port=config.get('CPD', 'cpd_port'),
            user=config.get('CPD', 'cpd_username'),
            password=config.get('CPD', 'password'),
            db_name=config.get('GENERAL', 'database')
        )
    print(fmt.format("Milvus Connection Established"))
    warnings.filterwarnings("ignore")
setup_milvus_connection()