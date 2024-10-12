import warnings,configparser
from urllib.parse import urlparse
from pymilvus import MilvusClient, connections
import pkg_resources

# Authentication enabled with the root user

FMT = "\n=== {:30} ===\n"
FILE_PATH = pkg_resources.resource_filename("milvus_library", "config.properties")


def setup_milvus_client_connection():
    config = configparser.ConfigParser()
    config.read(FILE_PATH)
    platform = config.get('GENERAL', 'platform')
    url = config.get('MILVUS', 'milvus_grpc_url')
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    db_name = config.get('GENERAL', 'database')
    

    print(FMT.format("Establishing the Milvus connection via Milvus Client"))

    if platform == "saas":
        saas_user = config.get('SAAS', 'saas_username')
        saas_pwd = config.get('SAAS', 'password')

        client = MilvusClient(
            uri=f"https://{saas_user}:{saas_pwd}@{host}:{port}",
            db_name=db_name
        )

    elif platform == "cpd":
        cpd_user = config.get('CPD', 'cpd_username')
        cpd_pwd = config.get('CPD', 'password')
        cert_file = config.get('CPD', 'cpd_cert_path')

        client = MilvusClient(
            uri=f"https://{cpd_user}:{cpd_pwd}@{host}:{port}",
            server_pem_path=cert_file,
            db_name=db_name
        )
    
    print(FMT.format("Milvus Connection Established via MilvusClient"))
    return client

setup_milvus_client_connection()

def setup_milvus_orm_connection():
    config = configparser.ConfigParser()
    config.read(FILE_PATH)
    platform = config.get('GENERAL', 'platform')
    url = config.get('MILVUS', 'milvus_grpc_url')
    parsed_url = urlparse(url)

    print(FMT.format("Establishing the Milvus connection via ORM"))

    if platform == "saas":
        connections.connect(
            secure=True,
            host=parsed_url.hostname,
            port=parsed_url.port,
            server_name=parsed_url.hostname,
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

    print(FMT.format("Milvus Connection Established via ORM"))
    warnings.filterwarnings("ignore")
