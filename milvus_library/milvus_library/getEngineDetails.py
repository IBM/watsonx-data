import pkg_resources, requests, configparser, milvus_library.utils as utils, subprocess
import warnings
warnings.filterwarnings("ignore")
file_path = pkg_resources.resource_filename("milvus_library", "config.properties")
fmt = "\n=== {:30} ===\n"
def getEngineDetails(file_path):
    config=configparser.ConfigParser()
    config.read(file_path)
    token = utils.token(file_path)
    platform = config.get("GENERAL", "platform")


    print(fmt.format("Reading the Config Properties"))
    if(platform == 'cpd'):

        cpd_url = config.get("CPD", "cpd_url")

        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{cpd_url}/zen-data/v3/service_instances?add_on_type=watsonx-data", headers=headers, verify=False)

        json_data = response.json()

        instanceId = config.get("CPD", "instanceId")

        url = f"{cpd_url}/lakehouse/api/v2/milvus_services"

        headers = {

                "LhInstanceId": f"{instanceId}",
                "Authorization": f"Bearer {token}"
            }
        print(fmt.format(f"Sending the request to url: {url}"))
        response = requests.get(headers=headers, url=url, verify=False)
        
        json_data = response.json()

        httpsHost = json_data["milvus_services"][0]["https_host"]
        grpcHost = json_data["milvus_services"][0]["grpc_host"]
        serviceId = json_data["milvus_services"][0]["service_id"]

        config.set("MILVUS", "milvus_grpc_url", grpcHost)
        config.set("MILVUS", "milvus_rest_url", httpsHost)
        config.set("MILVUS", "service_id", serviceId)
        print(f"milvus_grpc_url: {grpcHost}")
        print(f"milvus_rest_url: {httpsHost}")
        print(f"milvus_service_id: {serviceId}")
        with open("config.properties", "w") as configfile:
            config.write(configfile)

        print(f"---Generating certificates for REST and gRPC connections---")

        grpc_cert_command = f'echo QUIT | openssl s_client -showcerts -connect {grpcHost}:443 | awk \'/-----BEGIN CERTIFICATE-----/ {{p=1}}; p; /-----END CERTIFICATE-----/ {{p=0}}\' > milvus-grpc.crt'
        subprocess.run(grpc_cert_command, shell=True)

        
        rest_cert_command = f'echo QUIT | openssl s_client -showcerts -connect {httpsHost}:443 | awk \'/-----BEGIN CERTIFICATE-----/ {{p=1}}; p; /-----END CERTIFICATE-----/ {{p=0}}\' > milvus-rest.crt'
        subprocess.run(rest_cert_command, shell=True)

    elif(platform == 'saas'):

        crn = config.get("SAAS", "crn")
        print(f"CRN: {crn}")
        saas_url = config.get("SAAS", "url")
        url = f"{saas_url}/lakehouse/api/v2/milvus_services"
        
        headers = {
            "AuthInstanceID": f"{crn}",
            "Authorization": f"Bearer {token}"
        }
        print(fmt.format(f"Sending the request to url: {url}"))
        response = requests.get(
            headers=headers,
            url=url,
            verify=False
        )

        json_data = response.json()
        print(fmt.format("API response received"))
        service_display_name = config.get("GENERAL","service_name")
        print(f"Service Display Name: {service_display_name}")
        service_data = next((service for service in json_data["milvus_services"] if service["service_display_name"] == service_display_name), None)
  
        grpc_host = service_data["grpc_host"]
        grpc_port = service_data["grpc_port"]
        https_port = service_data["https_port"]
        https_host = service_data["https_host"]
        serviceId = service_data["service_id"]

        grpc = f"grpc://{grpc_host}:{grpc_port}"
        rest = f"https://{https_host}:{https_port}"
        print(f"milvus_grpc_url: {grpc}")
        print(f"milvus_rest_url: {rest}")
        print(f"Service Id: {serviceId}")
        config.set("MILVUS", "milvus_grpc_url", grpc)
        config.set("MILVUS", "milvus_rest_url", rest)
        config.set("MILVUS", "service_id", serviceId)

        with open(file_path, 'w') as config_file:
                config.write(config_file)

    
getEngineDetails(file_path)