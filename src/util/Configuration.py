import os, yaml
from src.util.Database import Database

class Configuration():
    default_fang = "config/fang.yaml"
    default_ukraine = "config/ukraine.yaml"
    default_coaid = "config/coaid.yaml"
    default_hamas = "config/hamas.yaml"

    def __init__(self, config_file='config/ukraine.yaml'):

        self.root_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.base_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        print(self.base_folder)

        self.base_keys = {
            'root_folder' : self.root_folder,
            'base_folder' : self.base_folder
        }

        config_file_path = self.base_folder + "/" + config_file
        self.load_yaml(config_file_path)

        # create data dir if not exists
        if not os.path.exists(self.data_folder_path):
            os.makedirs(self.data_folder_path)

        # create dataset dir if not exists
        if not os.path.exists(self.data_dataset_folder_path):
            os.makedirs(self.data_dataset_folder_path)

        # Load Twitter Credentials
        if os.path.exists(self.twitterv2_credential_file_path):
            self.load_yaml(self.twitterv2_credential_file_path)


    def load_yaml(self, file_path):
        with open(file_path, "r") as file:
            try:
                yaml_config = yaml.safe_load(file)         
                for config_key, config_value in yaml_config.items():
                    # apply base keys to config
                    f_dict = {}
                    for key, value in self.base_keys.items():
                        if type(config_value) == str and key in config_value:
                            f_dict[key] = value
                    if len(f_dict.keys()) > 0:
                        setattr(self, config_key, config_value.format(**f_dict))
                    else:
                        setattr(self, config_key, config_value)
            except yaml.YAMLError as exc:
                print(exc)

    def get_db(self):
        return Database(connection_params={
            "host" : self.DB_host, 
            "user" : self.DB_user, 
            "password" : self.DB_password, 
            "database" : self.DB_database
        })




