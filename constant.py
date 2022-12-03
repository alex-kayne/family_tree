import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent
DATETIME_FORMAT = '%m.%d.%Y %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

TREE_JS_FILE_PATH = BASE_DIR / 'templates' / 'familytree.js'

CLIENT_SECRETS_FILE = BASE_DIR / 'client_secret.json'

SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile',
          'openid']

OAUTH2CALLBACK_PATH = 'oauth2callback'
