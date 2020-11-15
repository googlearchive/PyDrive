OAuth made easy
===============

Authentication in two lines
---------------------------

OAuth2.0 is complex and difficult to start with. To make it more simple,
*PyDrive2* makes all authentication into just two lines.

.. code-block:: python

    from pydrive2.auth import GoogleAuth

    gauth = GoogleAuth()
    # Create local webserver and auto handles authentication.
    gauth.LocalWebserverAuth()

    # Or use the CommandLineAuth(), which provides you with a link to paste
    # into your browser. The site it leads to then provides you with an
    # authentication token which you paste into the command line.
    # Commented out as it is an alternative to the LocalWebserverAuth() above,
    # and someone will just copy-paste the entire thing into their editor.

    # gauth.CommandLineAuth()

To make this code work, you need to download the application configurations file
from APIs Console. Take a look at quickstart_ for detailed instructions.

`LocalWebserverAuth()`_ is a built-in method of `GoogleAuth`_ which sets up
local webserver to automatically receive authentication code from user and
authorizes by itself. You can also use `CommandLineAuth()`_ which manually
takes code from user at command line.

.. _quickstart: ./quickstart.html#authentication
.. _`LocalWebserverAuth()`: ./pydrive2.html#pydrive2.auth.GoogleAuth.LocalWebserverAuth
.. _`GoogleAuth`: ./pydrive2.html#pydrive2.auth.GoogleAuth
.. _`CommandLineAuth()`: ./pydrive2.html#pydrive.auth.GoogleAuth.CommandLineAuth

Automatic and custom authentication with *settings.yaml*
--------------------------------------------------------

Read this section if you need a custom authentication flow, **such as silent
authentication on a remote machine**. For an example of such a setup have a look
at `Sample settings.yaml`_.

OAuth is complicated and it requires a lot of settings. By default,
when you don't provide any settings, *PyDrive* will automatically set default
values which works for most of the cases. Here are some default settings.

- Read client configuration from file *client_secrets.json*
- OAuth scope: :code:`https://www.googleapis.com/auth/drive`
- Don't save credentials
- Don't retrieve refresh token

However, you might want to customize these settings while maintaining two lines
of clean code. If that is the case, you can make *settings.yaml* file in your
working directory and *PyDrive* will read it to customize authentication
behavior.

These are all the possible fields of a *settings.yaml* file:

.. code-block:: python

    client_config_backend: {{str}}
    client_config_file: {{str}}
    client_config:
      client_id: {{str}}
      client_secret: {{str}}
      auth_uri: {{str}}
      token_uri: {{str}}
      redirect_uri: {{str}}
      revoke_uri: {{str}}

    save_credentials: {{bool}}
    save_credentials_backend: {{str}}
    save_credentials_file: {{str}}

    get_refresh_token: {{bool}}

    oauth_scope: {{list of str}}

Fields explained:

:client_config_backend (str): From where to read client configuration(API application settings such as client_id and client_secrets) from. Valid values are 'file' and 'settings'. **Default**: 'file'. **Required**: No.
:client_config_file (str): When *client_config_backend* is 'file', path to the file containing client configuration. **Default**: 'client_secrets.json'. **Required**: No.
:client_config (dict): Place holding dictionary for client configuration when *client_config_backend* is 'settings'. **Required**: Yes, only if *client_config_backend* is 'settings'
:client_config['client_id'] (str): Client ID of the application. **Required**: Yes, only if *client_config_backend* is 'settings'
:client_config['client_secret'] (str): Client secret of the application. **Required**: Yes, only if *client_config_backend* is 'settings'
:client_config['auth_uri'] (str): The authorization server endpoint URI. **Default**: 'https://accounts.google.com/o/oauth2/auth'. **Required**: No.
:client_config['token_uri'] (str): The token server endpoint URI. **Default**: 'https://accounts.google.com/o/oauth2/token'. **Required**: No.
:client_config['redirect_uri'] (str): Redirection endpoint URI. **Default**: 'urn:ietf:wg:oauth:2.0:oob'. **Required**: No.
:client_config['revoke_uri'] (str): Revoke endpoint URI. **Default**: None. **Required**: No.
:save_credentials (bool): True if you want to save credentials. **Default**: False. **Required**: No.
:save_credentials_backend (str): Backend to save credentials to. 'file' is the only valid value for now. **Default**: 'file'. **Required**: No.
:save_credentials_file (str): Destination of credentials file. **Required**: Yes, only if *save_credentials_backend* is 'file'.
:get_refresh_token (bool): True if you want to retrieve refresh token along with access token. **Default**: False. **Required**: No.
:oauth_scope (list of str): OAuth scope to authenticate. **Default**: ['https://www.googleapis.com/auth/drive']. **Required**: No.

Sample *settings.yaml*
______________________

::

    client_config_backend: settings
    client_config:
      client_id: 9637341109347.apps.googleusercontent.com
      client_secret: psDskOoWr1P602PXRTHi

    save_credentials: True
    save_credentials_backend: file
    save_credentials_file: credentials.json

    get_refresh_token: True

    oauth_scope:
      - https://www.googleapis.com/auth/drive.file
      - https://www.googleapis.com/auth/drive.install
      - https://www.googleapis.com/auth/drive.metadata

Building your own authentication flow
-------------------------------------

You might want to build your own authentication flow. For example, you might
want to integrate your existing website with Drive API. In that case, you can
customize authentication flow as follwing:

1. Get authentication Url from `GetAuthUrl()`_.
2. Ask users to visit the authentication Url and grant access to your application. Retrieve authentication code manually by user or automatically by building your own oauth2callback.
3. Call `Auth(code)`_ with the authentication code you retrieved from step 2.

Your *settings.yaml* will work for your customized authentication flow, too.

Here is a sample code for your customized authentication flow

.. code-block:: python

    from pydrive2.auth import GoogleAuth

    gauth = GoogleAuth()
    auth_url = gauth.GetAuthUrl() # Create authentication url user needs to visit
    code = AskUserToVisitLinkAndGiveCode(auth_url) # Your customized authentication flow
    gauth.Auth(code) # Authorize and build service from the code

.. _`GetAuthUrl()`: ./pydrive2.html#pydrive2.auth.GoogleAuth.GetAuthUrl
.. _`Auth(code)`: ./pydrive2.html#pydrive2.auth.GoogleAuth.Auth
