from yaml import load
from yaml import YAMLError
try:
  from yaml import CLoader as Loader
except ImportError:
  from yaml import Loader

SETTINGS_FILE = 'settings.yaml'
SETTINGS_STRUCT = {
    'client_config_backend': {
        'type': str,
        'required': True,
        'default': 'file',
        'dependency': [
            {
                'value': 'file',
                'attribute': ['client_config_file']
            },
            {
                'value': 'settings',
                'attribute': ['client_config']
            },
            {
                'value': 'service',
                'attribute': ['service_config']
            }
        ]
    },
    'save_credentials': {
        'type': bool,
        'required': True,
        'default': False,
        'dependency': [
            {
                'value': True,
                'attribute': ['save_credentials_backend']
            }
        ]
    },
    'get_refresh_token': {
        'type': bool,
        'required': False,
        'default': False
    },
    'client_config_file': {
        'type': str,
        'required': False,
        'default': 'client_secrets.json'
    },
    'save_credentials_backend': {
        'type': str,
        'required': False,
        'dependency': [
            {
                'value': 'file',
                'attribute': ['save_credentials_file']
            }
        ]
    },
    'client_config': {
        'type': dict,
        'required': False,
        'struct': {
            'client_id': {
                'type': str,
                'required': True
            },
            'client_secret': {
                'type': str,
                'required': True
            },
            'auth_uri': {
                'type': str,
                'required': True,
                'default': 'https://accounts.google.com/o/oauth2/auth'
            },
            'token_uri': {
                'type': str,
                'required': True,
                'default': 'https://accounts.google.com/o/oauth2/token'
            },
            'redirect_uri': {
                'type': str,
                'required': True,
                'default': 'urn:ietf:wg:oauth:2.0:oob'
            },
            'revoke_uri': {
                'type': str,
                'required': True,
                'default': None
            }
        }
    },
    'service_config': {
        'type': dict,
        'required': False,
        'struct': {
            'client_user_email': {
                'type': str,
                'required': True,
                'default': None
            },
            'client_service_email': {
                'type': str,
                'required': True
            },
            'client_pkcs12_file_path': {
                'type': str,
                'required': True
            }
        }
    },
    'oauth_scope': {
        'type': list,
        'required': True,
        'struct': str,
        'default': ['https://www.googleapis.com/auth/drive']
    },
    'save_credentials_file': {
        'type': str,
        'required': False,
    }
}


class SettingsError(IOError):
  """Error while loading/saving settings"""


class InvalidConfigError(IOError):
  """Error trying to read client configuration."""


def LoadSettingsFile(filename=SETTINGS_FILE):
  """Loads settings file in yaml format given file name.

  :param filename: path for settings file. 'settings.yaml' by default.
  :type filename: str.
  :raises: SettingsError
  """
  try:
    stream = open(filename, 'r')
    data = load(stream, Loader=Loader)
  except (YAMLError, IOError) as e:
    raise SettingsError(e)
  return data


def ValidateSettings(data):
  """Validates if current settings is valid.

  :param data: dictionary containing all settings.
  :type data: dict.
  :raises: InvalidConfigError
  """
  _ValidateSettingsStruct(data, SETTINGS_STRUCT)


def _ValidateSettingsStruct(data, struct):
  """Validates if provided data fits provided structure.

  :param data: dictionary containing settings.
  :type data: dict.
  :param struct: dictionary containing structure information of settings.
  :type struct: dict.
  :raises: InvalidConfigError
  """
  # Validate required elements of the setting.
  for key in struct:
    if struct[key]['required']:
      _ValidateSettingsElement(data, struct, key)


def _ValidateSettingsElement(data, struct, key):
  """Validates if provided element of settings data fits provided structure.

  :param data: dictionary containing settings.
  :type data: dict.
  :param struct: dictionary containing structure information of settings.
  :type struct: dict.
  :param key: key of the settings element to validate.
  :type key: str.
  :raises: InvalidConfigError
  """
  # Check if data exists. If not, check if default value exists.
  value = data.get(key)
  data_type = struct[key]['type']
  if value is None:
    try:
      default = struct[key]['default']
    except KeyError:
      raise InvalidConfigError('Missing required setting %s' % key)
    else:
      data[key] = default
  # If data exists, Check type of the data
  elif type(value) is not data_type:
    raise InvalidConfigError('Setting %s should be type %s' % (key, data_type))
  # If type of this data is dict, check if structure of the data is valid.
  if data_type is dict:
    _ValidateSettingsStruct(data[key], struct[key]['struct'])
  # If type of this data is list, check if all values in the list is valid.
  elif data_type is list:
    for element in data[key]:
      if type(element) is not struct[key]['struct']:
        raise InvalidConfigError('Setting %s should be list of %s' %
                                 (key, struct[key]['struct']))
  # Check dependency of this attribute.
  dependencies = struct[key].get('dependency')
  if dependencies:
    for dependency in dependencies:
      if value == dependency['value']:
        for reqkey in dependency['attribute']:
          _ValidateSettingsElement(data, struct, reqkey)
