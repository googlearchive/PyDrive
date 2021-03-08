import os
import unittest
import time
import pytest

from pydrive2.auth import GoogleAuth
from pydrive2.test.test_util import (
    setup_credentials,
    delete_file,
    settings_file_path,
)


class GoogleAuthTest(unittest.TestCase):
    """Tests basic OAuth2 operations of auth.GoogleAuth."""

    @classmethod
    def setup_class(cls):
        setup_credentials()

    @pytest.mark.manual
    def test_01_LocalWebserverAuthWithClientConfigFromFile(self):
        # Delete old credentials file
        delete_file("credentials/1.dat")
        # Test if authentication works with config read from file
        ga = GoogleAuth(settings_file_path("test_oauth_test_01.yaml"))
        ga.LocalWebserverAuth()
        self.assertEqual(ga.access_token_expired, False)
        # Test if correct credentials file is created
        self.CheckCredentialsFile("credentials/1.dat")
        time.sleep(1)

    @pytest.mark.manual
    def test_02_LocalWebserverAuthWithClientConfigFromSettings(self):
        # Delete old credentials file
        delete_file("credentials/2.dat")
        # Test if authentication works with config read from settings
        ga = GoogleAuth(settings_file_path("test_oauth_test_02.yaml"))
        ga.LocalWebserverAuth()
        self.assertEqual(ga.access_token_expired, False)
        # Test if correct credentials file is created
        self.CheckCredentialsFile("credentials/2.dat")
        time.sleep(1)

    @pytest.mark.manual
    def test_03_LocalWebServerAuthWithNoCredentialsSaving(self):
        # Delete old credentials file
        delete_file("credentials/3.dat")
        # Provide wrong credentials file
        ga = GoogleAuth(settings_file_path("test_oauth_test_03.yaml"))
        ga.LocalWebserverAuth()
        self.assertEqual(ga.access_token_expired, False)
        # Test if correct credentials file is created
        self.CheckCredentialsFile("credentials/3.dat", no_file=True)
        time.sleep(1)

    @pytest.mark.manual
    def test_04_CommandLineAuthWithClientConfigFromFile(self):
        # Delete old credentials file
        delete_file("credentials/4.dat")
        # Test if authentication works with config read from file
        ga = GoogleAuth(settings_file_path("test_oauth_test_04.yaml"))
        ga.CommandLineAuth()
        self.assertEqual(ga.access_token_expired, False)
        # Test if correct credentials file is created
        self.CheckCredentialsFile("credentials/4.dat")
        time.sleep(1)

    @pytest.mark.manual
    def test_05_ConfigFromSettingsWithoutOauthScope(self):
        # Test if authentication works without oauth_scope
        ga = GoogleAuth(settings_file_path("test_oauth_test_05.yaml"))
        ga.LocalWebserverAuth()
        self.assertEqual(ga.access_token_expired, False)
        time.sleep(1)

    @pytest.mark.skip(reason="P12 authentication is deprecated")
    def test_06_ServiceAuthFromSavedCredentialsP12File(self):
        setup_credentials("credentials/6.dat")
        ga = GoogleAuth(settings_file_path("test_oauth_test_06.yaml"))
        ga.ServiceAuth()
        self.assertEqual(ga.access_token_expired, False)
        time.sleep(1)

    def test_07_ServiceAuthFromSavedCredentialsJsonFile(self):
        # Have an initial auth so that credentials/7.dat gets saved
        ga = GoogleAuth(settings_file_path("test_oauth_test_07.yaml"))
        ga.ServiceAuth()
        self.assertTrue(os.path.exists(ga.settings["save_credentials_file"]))

        # Secondary auth should be made only using the previously saved
        # login info
        ga = GoogleAuth(settings_file_path("test_oauth_test_07.yaml"))
        ga.ServiceAuth()

        self.assertEqual(ga.access_token_expired, False)
        time.sleep(1)

    def CheckCredentialsFile(self, credentials, no_file=False):
        ga = GoogleAuth(settings_file_path("test_oauth_default.yaml"))
        ga.LoadCredentialsFile(credentials)
        self.assertEqual(ga.access_token_expired, no_file)


if __name__ == "__main__":
    unittest.main()
