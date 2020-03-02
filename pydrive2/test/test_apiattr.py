import unittest

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.test.test_util import (
    pydrive_retry,
    setup_credentials,
    settings_file_path,
)


class ApiAttributeTest(unittest.TestCase):
    """Test ApiAttr functions.
    """

    @classmethod
    def setup_class(cls):
        setup_credentials()

    def test_UpdateMetadataNotInfinitelyNesting(self):
        # Verify 'metadata' field present.
        self.assertTrue(self.file1.metadata is not None)
        pydrive_retry(self.file1.UpdateMetadata)

        # Verify 'metadata' field still present.
        self.assertTrue(self.file1.metadata is not None)
        # Ensure no 'metadata' field in 'metadata' (i.e. nested).
        self.assertTrue("metadata" not in self.file1.metadata)

    def setUp(self):
        ga = GoogleAuth(settings_file_path("default.yaml"))
        ga.ServiceAuth()
        self.drive = GoogleDrive(ga)
        self.file1 = self.drive.CreateFile()
        pydrive_retry(self.file1.Upload)

    def tearDown(self):
        pydrive_retry(self.file1.Delete)


if __name__ == "__main__":
    unittest.main()
