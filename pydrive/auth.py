import socket
import webbrowser
import httplib2
import oauth2client.clientsecrets as clientsecrets

from apiclient.discovery import build
from functools import wraps
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OOB_CALLBACK_URN
from oauth2client.file import Storage
from oauth2client.file import CredentialsFileSymbolicLinkError
from oauth2client.tools import ClientRedirectHandler
from oauth2client.tools import ClientRedirectServer
from oauth2client.util import scopes_to_string
from .apiattr import ApiAttribute
from .apiattr import ApiAttributeMixin
from .settings import LoadSettingsFile
from .settings import ValidateSettings
from .settings import SettingsError
from .settings import InvalidConfigError


class AuthError(Exception):
    """Base error for authentication/authorization errors."""


class InvalidCredentialsError(IOError):
    """Error trying to read credentials file."""


class AuthenticationRejected(AuthError):
    """User rejected authentication."""


class AuthenticationError(AuthError):
    """General authentication error."""


class RefreshError(AuthError):
    """Access token refresh error."""

def LoadAuth(decoratee):
    """Decorator to check if the auth is valid and loads auth if not."""
    @wraps(decoratee)
    def _decorated(self, *args, **kwargs):
        if self.auth is None:    # Initialize auth if needed.
            self.auth = GoogleAuth()
        if self.auth.access_token_expired:
            self.auth.LocalWebserverAuth()
        if self.auth.service is None:    # Check if drive api is built.
            self.auth.Authorize()
        return decoratee(self, *args, **kwargs)
    return _decorated

def CheckAuth(decoratee):
    """Decorator to check if it requires OAuth2 flow request."""
    @wraps(decoratee)
    def _decorated(self, *args, **kwargs):
        dirty = False
        code = None
        save_credentials = self.settings.get('save_credentials')
        if self.credentials is None and save_credentials:
            self.LoadCredentials()
        if self.flow is None:
            self.GetFlow()
        if self.credentials is None:
            code = decoratee(self, *args, **kwargs)
            dirty = True
        else:
            if self.access_token_expired:
                if self.credentials.refresh_token is not None:
                    self.Refresh()
                else:
                    code = decoratee(self, *args, **kwargs)
                dirty = True
        if code is not None:
            self.Auth(code)
        if dirty and save_credentials:
            self.SaveCredentials()
    return _decorated


class GoogleAuth(ApiAttributeMixin, object):
    """Wrapper class for oauth2client library in google-api-python-client.

    Loads all settings and credentials from one 'settings.yaml' file
    and performs common OAuth2.0 related functionality such as authentication
    and authorization.
    """
    DEFAULT_SETTINGS = {
            'client_config_backend': 'file',
            'client_config_file': 'client_secrets.json',
            'save_credentials': False,
            'oauth_scope': ['https://www.googleapis.com/auth/drive']
            }
    CLIENT_CONFIGS_LIST = ['client_id', 'client_secret', 'auth_uri',
                                                 'token_uri', 'revoke_uri', 'redirect_uri']
    settings = ApiAttribute('settings')
    client_config = ApiAttribute('client_config')
    flow = ApiAttribute('flow')
    credentials = ApiAttribute('credentials')
    http = ApiAttribute('http')
    service = ApiAttribute('service')

    def __init__(self, settings_file='settings.yaml'):
        """Create an instance of GoogleAuth.

        This constructor just sets the path of settings file.
        It does not actually read the file.

        :param settings_file: path of settings file. 'settings.yaml' by default.
        :type settings_file: str.
        """
        ApiAttributeMixin.__init__(self)
        self.client_config = {}
        try:
            self.settings = LoadSettingsFile(settings_file)
        except SettingsError:
            self.settings = self.DEFAULT_SETTINGS
        else:
            if self.settings is None:
                self.settings = self.DEFAULT_SETTINGS
            else:
                ValidateSettings(self.settings)

    @property
    def access_token_expired(self):
        """Checks if access token doesn't exist or is expired.

        :returns: bool -- True if access token doesn't exist or is expired.
        """
        if self.credentials is None:
            return True
        return self.credentials.access_token_expired

    @CheckAuth
    def LocalWebserverAuth(self, host_name='localhost',
                                                 port_numbers=[8080, 8090]):
        """Authenticate and authorize from user by creating local webserver and
        retrieving authentication code.

        This function is not for webserver application. It creates local webserver
        for user from standalone application.

        :param host_name: host name of the local webserver.
        :type host_name: str.
        :param port_numbers: list of port numbers to be tried to used.
        :type port_numbers: list.
        :returns: str -- code returned from local webserver
        :raises: AuthenticationRejected, AuthenticationError
        """
        success = False
        port_number = 0
        for port in port_numbers:
            port_number = port
            try:
                httpd = ClientRedirectServer((host_name, port), ClientRedirectHandler)
            except socket.error, e:
                pass
            else:
                success = True
                break
        if success:
            oauth_callback = 'http://%s:%s/' % (host_name, port_number)
        else:
            print 'Failed to start a local webserver. Please check your firewall'
            print 'settings and locally running programs that may be blocking or'
            print 'using configured ports. Default ports are 8080 and 8090.'
            raise AuthenticationError()
        self.flow.redirect_uri = oauth_callback
        authorize_url = self.GetAuthUrl()
        webbrowser.open(authorize_url, new=1, autoraise=True)
        print 'Your browser has been opened to visit:'
        print
        print '        ' + authorize_url
        print
        httpd.handle_request()
        if 'error' in httpd.query_params:
            print 'Authentication request was rejected'
            raise AuthenticationRejected('User rejected authentication')
        if 'code' in httpd.query_params:
            return httpd.query_params['code']
        else:
            print 'Failed to find "code" in the query parameters of the redirect.'
            print 'Try command-line authentication'
            raise AuthenticationError('No code found in redirect')

    @CheckAuth
    def CommandLineAuth(self):
        """Authenticate and authorize from user by printing authentication url
        retrieving authentication code from command-line.

        :returns: str -- code returned from commandline.
        """
        self.flow.redirect_uri = OOB_CALLBACK_URN
        authorize_url = self.GetAuthUrl()
        print 'Go to the following link in your browser:'
        print
        print '        ' + authorize_url
        print
        return raw_input('Enter verification code: ').strip()

    def LoadCredentials(self, backend=None):
        """Loads credentials or create empty credentials if it doesn't exist.

        :param backend: target backend to save credential to.
        :type backend: str.
        :raises: InvalidConfigError
        """
        if backend is None:
            backend = self.settings.get('save_credentials_backend')
            if backend is None:
                raise InvalidConfigError('Please specify credential backend')
        if backend == 'file':
            self.LoadCredentialsFile()
        else:
            raise InvalidConfigError('Unknown save_credentials_backend')

    def LoadCredentialsFile(self, credentials_file=None):
        """Loads credentials or create empty credentials if it doesn't exist.

        Loads credentials file from path in settings if not specified.

        :param credentials_file: path of credentials file to read.
        :type credentials_file: str.
        :raises: InvalidConfigError, InvalidCredentialsError
        """
        if credentials_file is None:
            credentials_file = self.settings.get('save_credentials_file')
            if credentials_file is None:
                raise InvalidConfigError('Please specify credentials file to read')
        try:
            storage = Storage(credentials_file)
            self.credentials = storage.get()
        except CredentialsFileSymbolicLinkError:
            raise InvalidCredentialsError('Credentials file cannot be symbolic link')

    def SaveCredentials(self, backend=None):
        """Saves credentials according to specified backend.

        If you have any specific credentials backend in mind, don't use this
        function and use the corresponding function you want.

        :param backend: backend to save credentials.
        :type backend: str.
        :raises: InvalidConfigError
        """
        if backend is None:
            backend = self.settings.get('save_credentials_backend')
            if backend is None:
                raise InvalidConfigError('Please specify credential backend')
        if backend == 'file':
            self.SaveCredentialsFile()
        else:
            raise InvalidConfigError('Unknown save_credentials_backend')

    def SaveCredentialsFile(self, credentials_file=None):
        """Saves credentials to the file in JSON format.

        :param credentials_file: destination to save file to.
        :type credentials_file: str.
        :raises: InvalidConfigError, InvalidCredentialsError
        """
        if self.credentials is None:
            raise InvalidCredentialsError('No credentials to save')
        if credentials_file is None:
            credentials_file = self.settings.get('save_credentials_file')
            if credentials_file is None:
                raise InvalidConfigError('Please specify credentials file to read')
        try:
            storage = Storage(credentials_file)
            storage.put(self.credentials)
            self.credentials.set_store(storage)
        except CredentialsFileSymbolicLinkError:
            raise InvalidCredentialsError('Credentials file cannot be symbolic link')

    def LoadClientConfig(self, backend=None):
        """Loads client configuration according to specified backend.

        If you have any specific backend to load client configuration from in mind,
        don't use this function and use the corresponding function you want.

        :param backend: backend to load client configuration from.
        :type backend: str.
        :raises: InvalidConfigError
        """
        if backend is None:
            backend = self.settings.get('client_config_backend')
            if backend is None:
                raise InvalidConfigError('Please specify client config backend')
        if backend == 'file':
            self.LoadClientConfigFile()
        elif backend == 'settings':
            self.LoadClientConfigSettings()
        else:
            raise InvalidConfigError('Unknown client_config_backend')

    def LoadClientConfigFile(self, client_config_file=None):
        """Loads client configuration file downloaded from APIs console.

        Loads client config file from path in settings if not specified.

        :param client_config_file: path of client config file to read.
        :type client_config_file: str.
        :raises: InvalidConfigError
        """
        if client_config_file is None:
            client_config_file = self.settings['client_config_file']
        try:
            client_type, client_info = clientsecrets.loadfile(client_config_file)
        except clientsecrets.InvalidClientSecretsError, error:
            raise InvalidConfigError('Invalid client secrets file %s' % error)
        if not client_type in (clientsecrets.TYPE_WEB,
                                                     clientsecrets.TYPE_INSTALLED):
            raise InvalidConfigError('Unknown client_type of client config file')
        try:
            config_index = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            for config in config_index:
                self.client_config[config] = client_info[config]
            self.client_config['revoke_uri'] = client_info.get('revoke_uri')
            self.client_config['redirect_uri'] = client_info['redirect_uris'][0]
        except KeyError:
            raise InvalidConfigError('Insufficient client config in file')

    def LoadClientConfigSettings(self):
        """Loads client configuration from settings file.

        :raises: InvalidConfigError
        """
        for config in self.CLIENT_CONFIGS_LIST:
            try:
                self.client_config[config] = self.settings['client_config'][config]
            except KeyError:
                raise InvalidConfigError('Insufficient client config in settings')

    def GetFlow(self):
        """Gets Flow object from client configuration.

        :raises: InvalidConfigError
        """
        if not all(config in self.client_config \
                             for config in self.CLIENT_CONFIGS_LIST):
            self.LoadClientConfig()
        constructor_kwargs = {
                'redirect_uri': self.client_config['redirect_uri'],
                'auth_uri': self.client_config['auth_uri'],
                'token_uri': self.client_config['token_uri'],
        }
        if self.client_config['revoke_uri'] is not None:
            constructor_kwargs['revoke_uri'] = self.client_config['revoke_uri']
        self.flow = OAuth2WebServerFlow(
                self.client_config['client_id'],
                self.client_config['client_secret'],
                scopes_to_string(self.settings['oauth_scope']),
                **constructor_kwargs)
        if self.settings.get('get_refresh_token'):
            self.flow.params.update({'access_type': 'offline'})

    def Refresh(self):
        """Refreshes the access_token.

        :raises: RefreshError
        """
        if self.credentials is None:
            raise RefreshError('No credential to refresh.')
        if self.credentials.refresh_token is None:
            raise RefreshError('No refresh_token found.'
                                                 'Please set access_type of OAuth to offline.')
        if self.http is None:
            self.http = httplib2.Http()
        try:
            self.credentials.refresh(self.http)
        except AccessTokenRefreshError, error:
            raise RefreshError('Access token refresh failed: %s' % error)

    def GetAuthUrl(self):
        """Creates authentication url where user visits to grant access.

        :returns: str -- Authentication url.
        """
        if self.flow is None:
            self.GetFlow()
        return self.flow.step1_get_authorize_url()

    def Auth(self, code):
        """Authenticate, authorize, and build service.

        :param code: Code for authentication.
        :type code: str.
        :raises: AuthenticationError
        """
        self.Authenticate(code)
        self.Authorize()

    def Authenticate(self, code):
        """Authenticates given authentication code back from user.

        :param code: Code for authentication.
        :type code: str.
        :raises: AuthenticationError
        """
        if self.flow is None:
            self.GetFlow()
        try:
            self.credentials = self.flow.step2_exchange(code)
        except FlowExchangeError, e:
            raise AuthenticationError('OAuth2 code exchange failed: %s' % e)
        print 'Authentication successful.'

    def Authorize(self):
        """Authorizes and builds service.

        :raises: AuthenticationError
        """
        if self.http is None:
            self.http = httplib2.Http()
        if self.access_token_expired:
            raise AuthenticationError('No valid credentials provided to authorize')
        self.http = self.credentials.authorize(self.http)
        self.service = build('drive', 'v2', http=self.http)
