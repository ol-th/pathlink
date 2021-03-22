import configparser


def get_config():
    config = configparser.ConfigParser()
    config.read("server_config")

    if "mutations_db" not in config or "uri" not in config["mutations_db"]:
        print("Server config not found!")
        return None

    return config
