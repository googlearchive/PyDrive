import unittest
import os
import time
import pytest

from pydrive2.auth import GoogleAuth
from pydrive2.test.test_util import setup_credentials


class GoogleAuthTest(unittest.TestCase):
  """Tests basic OAuth2 operations of auth.GoogleAuth."""

  @pytest.mark.manual
  def test_01_LocalWebserverAuthWithClientConfigFromFile(self):
    # Delete old credentials file
    self.DeleteOldCredentialsFile('credentials/1.dat')
    # Test if authentication works with config read from file
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_test_01.yaml')
    ga.LocalWebserverAuth()
    self.assertEqual(ga.access_token_expired, False)
    # Test if correct credentials file is created
    self.CheckCredentialsFile('credentials/1.dat')
    time.sleep(1)

  @pytest.mark.manual
  def test_02_LocalWebserverAuthWithClientConfigFromSettings(self):
    # Delete old credentials file
    self.DeleteOldCredentialsFile('credentials/2.dat')
    # Test if authentication works with config read from settings
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_test_02.yaml')
    ga.LocalWebserverAuth()
    self.assertEqual(ga.access_token_expired, False)
    # Test if correct credentials file is created
    self.CheckCredentialsFile('credentials/2.dat')
    time.sleep(1)

  @pytest.mark.manual
  def test_03_LocalWebServerAuthWithNoCredentialsSaving(self):
    # Delete old credentials file
    self.DeleteOldCredentialsFile('credentials/4.dat')
    # Provide wrong credentials file
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_test_03.yaml')
    ga.LocalWebserverAuth()
    self.assertEqual(ga.access_token_expired, False)
    # Test if correct credentials file is created
    self.CheckCredentialsFile('credentials/4.dat', no_file=True)
    time.sleep(1)

  @pytest.mark.manual
  def test_04_CommandLineAuthWithClientConfigFromFile(self):
    # Delete old credentials file
    self.DeleteOldCredentialsFile('credentials/1.dat')
    # Test if authentication works with config read from file
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_test_04.yaml')
    ga.CommandLineAuth()
    self.assertEqual(ga.access_token_expired, False)
    # Test if correct credentials file is created
    self.CheckCredentialsFile('credentials/1.dat')
    time.sleep(1)

  @pytest.mark.manual
  def test_05_ConfigFromSettingsWithoutOauthScope(self):
    # Test if authentication works without oauth_scope
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_test_05.yaml')
    ga.LocalWebserverAuth()
    self.assertEqual(ga.access_token_expired, False)
    time.sleep(1)

  def test_06_ServiceAuthFromSavedCredentialsFile(self):
    setup_credentials("credentials/6.dat")
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_test_06.yaml')
    ga.ServiceAuth()
    self.assertEqual(ga.access_token_expired, False)
    time.sleep(1)

  def DeleteOldCredentialsFile(self, credentials):
    try:
      os.remove(credentials)
    except OSError:
      pass

  def CheckCredentialsFile(self, credentials, no_file=False):
    ga = GoogleAuth('pydrive2/test/settings/test_oauth_default.yaml')
    ga.LoadCredentialsFile(credentials)
    self.assertEqual(ga.access_token_expired, no_file)

if __name__ == '__main__':
  unittest.main()
