import unittest

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError

class ApiAttributeTest(unittest.TestCase):
    """Test ApiAttr functions.
    """
    ga = GoogleAuth('settings/test1.yaml')
    ga.LocalWebserverAuth()
    first_file = 'a.png'
    second_file = 'b.png'

    def test_UpdateMetadataNotInfinitelyNesting(self):
        # Verify 'metadata' field present.
        self.assertTrue(self.file1.metadata is not None)
        self.file1.UpdateMetadata()
        self.file1.UpdateMetadata()

        # Verify 'metadata' field still present.
        self.assertTrue(self.file1.metadata is not None)
        # Ensure no 'metadata' field in 'metadata' (i.e. nested).
        self.assertTrue('metadata' not in self.file1.metadata)

    def setUp(self):
        self.drive = GoogleDrive(self.ga)
        self.file1 = self.drive.CreateFile()
        self.file1.Upload()

    def tearDown(self):
        self.file1.Delete()

if __name__ == '__main__':
    unittest.main()