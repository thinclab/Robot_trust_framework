"""
File to read and update configuration for a user
If file does not exist create a configuration
yaml is file type for configuration
"""
import os
import sys
import yaml
from utils import *
DIR_NAME = os.path.dirname(__file__)

class ConfigManger(object):

    def __init__(self, username):
        """
        Creates configuration in current working directory config folder
        :param username:configuration file name
        """
        self.user = username
        self.config_path = os.path.join(DIR_NAME, "config", username + ".yaml")
        print(DIR_NAME)
        self.config = None

    def fetch_config(self):
        """
        Function  to create a default configuration if not exists for a user
        If exists read the configuration and fetch the data
        @return: the config data
        """

        if not os.path.isfile(self.config_path):
            # Data to be written
            try:

                if not os.path.isdir(os.path.dirname(self.config_path)):
                    os.makedirs(os.path.dirname(self.config_path))
                self.config = {
                    ATTITUDE: 1,
                    RESPONSE_TIME: 2,
                    KINSHIP: None,
                    PREDICTOR_THRESHOLD: 0.5,
                    POSITIVE_EXP_COUNT: 0,
                    NEGATIVE_EXP_COUNT: 0,
                    # GOALS_ACHIEVED: 0,
                    MISSIONS_WORKED_TOGETHER: 0,
                    TRUST: 0,
                    DISTRUST: 0,
                    UNCERTAINTY: 0
                }
                # Serializing json
                yaml_object = yaml.dump(self.config, indent=4)

                # Writing to sample.json
                with open(self.config_path, "w") as outfile:
                    outfile.write(yaml_object)
            except Exception as e:
                print("Config creation failed due to", e)
                sys.exit(1)

        else:
            with open(self.config_path, "r") as outfile:
                self.config = yaml.safe_load(outfile)
        return self.config

    def update_config(self, key_value_map: dict):
        """
        updates the existing configuration with given dictionary
        @param key_value_map: dict
        """
        with open(self.config_path, "r") as outfile:
            self.config = yaml.safe_load(outfile)

        with open(self.config_path, "w") as outfile:
            self.config.update(key_value_map)
            yaml.dump(self.config, outfile)
