import requests, configparser, pkg_resources

file_path = pkg_resources.resource_filename("milvus_library", "config.properties")
def token(file_path):

    config=configparser.ConfigParser()
    config.read(file_path)
    platform = config.get('GENERAL','platform')
    URL = config.get('SAAS','url')

    if(platform =='cpd'):

        cpd_url = config.get('CPD','cpd_url')
        url= f"{cpd_url}/icp4d-api/v1/authorize"
        username = config.get('CPD','cpd_username')
        password = config.get('CPD', 'password')

        data = {

            "username": username,
            "password": password
        }

        response = requests.post(
            url=url,
            json=data,
            verify=False 
            )
        
        json_response = response.json()
        token = json_response.get('token')

    elif(platform =='saas'):

        username = config.get('SAAS','saas_username')
        instance_id = config.get('SAAS','crn')
        password = config.get('SAAS', 'password')
        url = f"{URL}/lakehouse/api/v2/auth/authenticate"

        data = {

            "username": username,
            "password": password,
            "instance_id": instance_id,
            "instance_name": ""

        }

        response = requests.post(
            url=url,
            json=data,
            verify=False  
            )

        json_response = response.json()
        token = json_response.get('accessToken')

    return token

token(file_path)
