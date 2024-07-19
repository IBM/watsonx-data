import requests, configparser, utils, subprocess

def getEngineDetails():

    config=configparser.ConfigParser()
    config.read('config.properties')
    token = utils.token()
    platform = config.get("GENERAL", "platform")

    if(platform == 'cpd'):

        cpd_url = config.get("CPD", "cpd_url")

        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{cpd_url}/zen-data/v3/service_instances?add_on_type=watsonx-data", headers=headers, verify=False)

        print(response.text)

        json_data = response.json()

        instanceId = config.get("CPD", "instanceId")

        url = f"{cpd_url}/lakehouse/api/v2/milvus_services"

        headers = {

                "LhInstanceId": f"{instanceId}",
                "Authorization": f"Bearer {token}"
            }
        
        response = requests.get(headers=headers, url=url, verify=False)
        
        print(f"\n\n{response.text}")
        json_data = response.json()

        httpsHost = json_data["milvus_services"][0]["https_host"]
        grpcHost = json_data["milvus_services"][0]["grpc_host"]
        serviceId = json_data["milvus_services"][0]["service_id"]

        config.add_section("MILVUS")
        config.set("MILVUS", "milvus_grpc_url", grpcHost)
        config.set("MIVLUS", "milvus_rest_url", httpsHost)
        config.set("MIVLUS", "service_id", serviceId)

        with open("config.properties", "w") as configfile:
            config.write(configfile)

        print(f"---Generating certificates for REST and gRPC connections---")

        grpc_cert_command = f'echo QUIT | openssl s_client -showcerts -connect {grpcHost}:443 | awk \'/-----BEGIN CERTIFICATE-----/ {{p=1}}; p; /-----END CERTIFICATE-----/ {{p=0}}\' > milvus-grpc.crt'
        subprocess.run(grpc_cert_command, shell=True)

        
        rest_cert_command = f'echo QUIT | openssl s_client -showcerts -connect {httpsHost}:443 | awk \'/-----BEGIN CERTIFICATE-----/ {{p=1}}; p; /-----END CERTIFICATE-----/ {{p=0}}\' > milvus-rest.crt'
        subprocess.run(rest_cert_command, shell=True)

    elif(platform == 'saas'):

        crn = config.get("SAAS", "crn")
        saas_url = config.get("SAAS", "url")
        url = f"{saas_url}/lakehouse/api/v2/milvus_services"

        headers = {
            "AuthInstanceID": f"{crn}",
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            headers=headers,
            url=url,
            verify=False
        )

        json_data = response.json()

        service_display_name = config.get("GENERAL","service_name")
        service_data = next((service for service in json_data["milvus_services"] if service["service_display_name"] == service_display_name), None)
  
        print(service_data)

        host = service_data["host_name"]
        grpc_port = service_data["grpc_port"]
        https_port = service_data["https_port"]
        serviceId = service_data["service_id"]

        grpc = f"grpc://{host}:{grpc_port}"
        rest = f"https://{host}:{https_port}"

        config.set("MILVUS", "milvus_grpc_url", grpc)
        config.set("MILVUS", "milvus_rest_url", rest)
        config.set("MILVUS", "service_id", serviceId)

        with open('config.properties', 'w') as configfile:
                config.write(configfile)

    
getEngineDetails()