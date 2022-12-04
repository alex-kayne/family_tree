import yaml
from constant import CONFIG_PATH, CLIENT_SECRETS_FILE
import sys
import json


def get_config(path):
    with open(path) as f:
        parsed_config = yaml.safe_load(f)
        with open(str(CLIENT_SECRETS_FILE)) as secret_file:
            if sys.argv[-1] == 'DEV':
                parsed_config['oauth_callback'] = json.load(secret_file)['web']['redirect_uris'][1]
            else:
                parsed_config['oauth_callback'] = json.load(secret_file)['web']['redirect_uris'][0]
        return parsed_config


config = get_config(CONFIG_PATH)
