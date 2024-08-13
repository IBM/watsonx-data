import pkg_resources, configparser

file_path = pkg_resources.resource_filename("milvus_library", "config.properties")

def getConfigProperties(file_path):
    config=configparser.ConfigParser()
    config.read(file_path)
    platform = input("Platform type: ")
    database = input("database: ")
    service_name = input("service_name: ")

    config.set("GENERAL", "platform", platform)
    config.set("GENERAL", "database", database)
    config.set("GENERAL", "service_name", service_name)

    if platform == "cpd":
    
        password = input("API key: ")
        cpd_url = input("cpd_url")
        instanceid = input("instanceid")
        config.set("CPD", "cpd_url", cpd_url)
        config.set("CPD", "instanceid", instanceid)

    if platform == "saas":

        # User inputs
        crn = input("Wxd crn: ")
        password = input("API key: ")
        config.set("SAAS", "crn", crn)
        config.set("SAAS", "password", password)
    # Print the values:
    print(f"crn: {crn}")
    print(f"password: {password}")
    print(f"service_name: {service_name}")
    print(f"platform: {platform}")
    print(f"database: {database}")

    # writing the config properties to the file
    with open(file_path, "w") as configfile:
        config.write(configfile)




