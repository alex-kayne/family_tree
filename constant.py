import pathlib

BASE_DIR = pathlib.Path(__file__).parent
DATETIME_FORMAT = '%m.%d.%Y %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

TREE_JS_FILE_PATH = BASE_DIR / 'templates'
CLIENT_SECRETS_FILE = BASE_DIR / 'client_secret.json'
CONFIG_PATH = BASE_DIR / 'config' / 'config.yaml'

SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile',
          'openid']

OAUTH2CALLBACK_FUN = 'oauth2callback'
