import requests, configparser, milvus_library.utils as utils
import warnings
warnings.filterwarnings("ignore")

def get_instance_id(token):

    token = utils.token()

    config=configparser.ConfigParser()
    config.read('config.properties')

    cpd_url = config.get("CPD", "cpd_url")

    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{cpd_url}/zen-data/v3/service_instances?add_on_type=watsonx-data", headers=headers, verify=False)

    json_data = response.json()

    instanceId = json_data["service_instances"][0]["id"]
    print(f"Instance ID:{instanceId}")
    config.set("CPD", "instanceId", instanceId)
    with open('config.properties', 'w') as configfile:
        config.write(configfile)