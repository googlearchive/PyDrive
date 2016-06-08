# -*- coding: utf-8 -*-
import unittest

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveTest(unittest.TestCase):
    """Tests basic operations on meta-data information of the linked Google Drive account.
    """

    ga = GoogleAuth('settings/test1.yaml')
    ga.LocalWebserverAuth()

    def test_01_About_Request(self):
        drive = GoogleDrive(self.ga)

        about_object = drive.GetAbout()
        self.assertTrue(about_object is not None, "About object not loading.")


if __name__ == '__main__':
    unittest.main()
