# -*- coding: utf-8 -*-
import unittest

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.test.test_util import (
    pydrive_retry,
    setup_credentials,
    settings_file_path,
)


class GoogleDriveTest(unittest.TestCase):
    """Tests basic operations on meta-data information of the linked Google Drive account.
    """

    @classmethod
    def setup_class(cls):
        setup_credentials()

        cls.ga = GoogleAuth(settings_file_path("default.yaml"))
        cls.ga.ServiceAuth()

    def test_01_About_Request(self):
        drive = GoogleDrive(self.ga)

        about_object = pydrive_retry(drive.GetAbout)
        self.assertTrue(about_object is not None, "About object not loading.")


if __name__ == "__main__":
    unittest.main()
