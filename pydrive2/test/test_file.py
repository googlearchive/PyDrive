# -*- coding: utf-8 -*-
import filecmp
import os
import unittest
import pytest
import sys
from io import BytesIO
from tempfile import mkdtemp
from time import time

from six.moves import range
import timeout_decorator
from concurrent.futures import ThreadPoolExecutor, as_completed
from googleapiclient import errors

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import ApiRequestError, GoogleDriveFile
from pydrive2.test import test_util
from pydrive2.test.test_util import (
    pydrive_retry,
    setup_credentials,
    create_file,
    delete_dir,
    delete_file,
    settings_file_path,
)


class GoogleDriveFileTest(unittest.TestCase):
    """Tests basic file operations of files.GoogleDriveFile.
  Upload and download of contents and metadata, and thread-safety checks.
  Equivalent to Files.insert, Files.update, Files.patch in Google Drive API.
  """

    @classmethod
    def setup_class(cls):
        setup_credentials()

        cls.tmpdir = mkdtemp()

        cls.ga = GoogleAuth(
            settings_file_path("default.yaml", os.path.join(cls.tmpdir, ""))
        )
        cls.ga.ServiceAuth()

    @classmethod
    def tearDownClass(cls):
        delete_dir(cls.tmpdir)

    @classmethod
    def getTempFile(cls, prefix="", content=""):
        filename = os.path.join(cls.tmpdir, prefix + str(time()))
        if content:
            create_file(filename, content)
        return filename

    def test_01_Files_Insert(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("firsttestfile")
        file1["title"] = filename
        pydrive_retry(file1.Upload)  # Files.insert

        self.assertEqual(file1.metadata["title"], filename)
        file2 = drive.CreateFile({"id": file1["id"]})  # Download file from id.
        self.assertEqual(file2["title"], filename)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_02_Files_Insert_Unicode(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile(u"첫번째 파일")
        file1["title"] = filename
        pydrive_retry(file1.Upload)  # Files.insert

        self.assertEqual(file1.metadata["title"], filename)
        file2 = drive.CreateFile({"id": file1["id"]})  # Download file from id.
        self.assertEqual(file2["title"], filename)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_03_Files_Insert_Content_String(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("secondtestfile")
        content = "hello world!"
        file1["title"] = filename
        file1.SetContentString(content)
        pydrive_retry(file1.Upload)  # Files.insert

        self.assertEqual(file1.GetContentString(), content)

        pydrive_retry(
            file1.FetchContent
        )  # Force download and double check content
        self.assertEqual(file1.metadata["title"], filename)
        self.assertEqual(file1.GetContentString(), content)

        file2 = drive.CreateFile({"id": file1["id"]})  # Download file from id.
        pydrive_retry(file2.FetchContent)
        self.assertEqual(file2.GetContentString(), content)
        self.assertEqual(file2.metadata["title"], filename)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_04_Files_Insert_Content_Unicode_String(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile(u"두번째 파일")
        content = u"안녕 세상아!"
        file1["title"] = filename
        file1.SetContentString(content)
        pydrive_retry(file1.Upload)  # Files.insert

        self.assertEqual(file1.GetContentString(), content)
        self.assertEqual(file1.metadata["title"], filename)
        pydrive_retry(
            file1.FetchContent
        )  # Force download and double check content.
        self.assertEqual(file1.GetContentString(), content)

        file2 = drive.CreateFile({"id": file1["id"]})  # Download file from id.
        pydrive_retry(file2.FetchContent)
        self.assertEqual(file2.GetContentString(), content)
        self.assertEqual(file2.metadata["title"], filename)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_05_Files_Insert_Content_File(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("filecontent")
        file1["title"] = filename
        contentFile = self.getTempFile("actual_content", "some string")
        file1.SetContentFile(contentFile)
        pydrive_retry(file1.Upload)  # Files.insert

        self.assertEqual(file1.metadata["title"], filename)
        pydrive_retry(
            file1.FetchContent
        )  # Force download and double check content.
        fileOut = self.getTempFile()
        pydrive_retry(file1.GetContentFile, fileOut)
        self.assertEqual(filecmp.cmp(contentFile, fileOut), True)

        file2 = drive.CreateFile({"id": file1["id"]})  # Download file from id.
        fileOut = self.getTempFile()
        pydrive_retry(file2.GetContentFile, fileOut)
        self.assertEqual(filecmp.cmp(contentFile, fileOut), True)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_06_Files_Patch(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("prepatchtestfile")
        newfilename = self.getTempFile("patchtestfile")
        file1["title"] = filename
        pydrive_retry(file1.Upload)  # Files.insert

        self.assertEqual(file1.metadata["title"], filename)
        file1["title"] = newfilename
        pydrive_retry(file1.Upload)  # Files.patch

        self.assertEqual(file1.metadata["title"], newfilename)
        file2 = drive.CreateFile({"id": file1["id"]})  # Download file from id.
        pydrive_retry(file2.FetchMetadata)
        self.assertEqual(file2.metadata["title"], newfilename)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_07_Files_Patch_Skipping_Content(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("prepatchtestfile")
        newfilename = self.getTempFile("patchtestfile")
        content = "hello world!"

        file1["title"] = filename
        file1.SetContentString(content)
        pydrive_retry(file1.Upload)  # Files.insert
        self.assertEqual(file1.metadata["title"], filename)

        file1["title"] = newfilename
        pydrive_retry(file1.Upload)  # Files.patch
        self.assertEqual(file1.metadata["title"], newfilename)
        self.assertEqual(file1.GetContentString(), content)
        self.assertEqual(file1.GetContentString(), content)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_08_Files_Update_String(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("preupdatetestfile")
        newfilename = self.getTempFile("updatetestfile")
        content = "hello world!"
        newcontent = "hello new world!"

        file1["title"] = filename
        file1.SetContentString(content)
        pydrive_retry(file1.Upload)  # Files.insert
        self.assertEqual(file1.metadata["title"], filename)
        self.assertEqual(file1.GetContentString(), content)

        pydrive_retry(
            file1.FetchContent
        )  # Force download and double check content.
        self.assertEqual(file1.GetContentString(), content)

        file1["title"] = newfilename
        file1.SetContentString(newcontent)
        pydrive_retry(file1.Upload)  # Files.update
        self.assertEqual(file1.metadata["title"], newfilename)
        self.assertEqual(file1.GetContentString(), newcontent)
        self.assertEqual(file1.GetContentString(), newcontent)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_09_Files_Update_File(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("preupdatetestfile")
        newfilename = self.getTempFile("updatetestfile")
        contentFile = self.getTempFile("actual_content", "some string")
        contentFile2 = self.getTempFile("actual_content_2", "some string")

        file1["title"] = filename
        file1.SetContentFile(contentFile)
        pydrive_retry(file1.Upload)  # Files.insert
        self.assertEqual(file1.metadata["title"], filename)

        pydrive_retry(
            file1.FetchContent
        )  # Force download and double check content.
        fileOut = self.getTempFile()
        pydrive_retry(file1.GetContentFile, fileOut)
        self.assertEqual(filecmp.cmp(contentFile, fileOut), True)

        file1["title"] = newfilename
        file1.SetContentFile(contentFile2)
        pydrive_retry(file1.Upload)  # Files.update
        self.assertEqual(file1.metadata["title"], newfilename)

        fileOut = self.getTempFile()
        pydrive_retry(file1.GetContentFile, fileOut)
        self.assertEqual(filecmp.cmp(contentFile2, fileOut), True)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_10_Files_Download_Service(self):
        """
        Tests that a fresh GoogleDrive object can correctly authenticate
        and download from a file ID.
        """
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile("prepatchtestfile")
        content = "hello world!"

        file1["title"] = filename
        file1.SetContentString(content)
        pydrive_retry(file1.Upload)  # Files.insert
        self.assertEqual(file1.metadata["title"], filename)
        fileOut1 = self.getTempFile()
        pydrive_retry(file1.GetContentFile, fileOut1)

        # fresh download-only instance
        auth = GoogleAuth(
            settings_file_path("default.yaml", os.path.join(self.tmpdir, ""))
        )
        auth.ServiceAuth()
        drive2 = GoogleDrive(auth)
        file2 = drive2.CreateFile({"id": file1["id"]})
        fileOut2 = self.getTempFile()
        pydrive_retry(file2.GetContentFile, fileOut2)
        self.assertEqual(filecmp.cmp(fileOut1, fileOut2), True)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_11_Files_Get_Content_Buffer(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        filename = self.getTempFile()
        content = "hello world!\ngoodbye, cruel world!"
        file1["title"] = filename
        file1.SetContentString(content)
        pydrive_retry(file1.Upload)  # Files.insert

        buffer1 = pydrive_retry(file1.GetContentIOBuffer)
        self.assertEqual(file1.metadata["title"], filename)
        self.assertEqual(len(buffer1), len(content))
        self.assertEqual(b"".join(iter(buffer1)).decode("ascii"), content)

        buffer2 = pydrive_retry(file1.GetContentIOBuffer, encoding="ascii")
        self.assertEqual(len(buffer2), len(content))
        self.assertEqual("".join(iter(buffer2)), content)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_12_Upload_Download_Empty_File(self):
        filename = os.path.join(self.tmpdir, str(time()))
        create_file(filename, "")

        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        file1.SetContentFile(filename)
        pydrive_retry(file1.Upload)

        fileOut1 = self.getTempFile()
        pydrive_retry(file1.GetContentFile, fileOut1)
        self.assertEqual(os.path.getsize(fileOut1), 0)

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_13_Upload_Download_Empty_String(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        file1.SetContentString("")
        pydrive_retry(file1.Upload)

        self.assertEqual(pydrive_retry(file1.GetContentString), "")

        # Force download and double check content
        pydrive_retry(file1.FetchContent)
        self.assertEqual(file1.GetContentString(), "")

        # Download file from id
        file2 = drive.CreateFile({"id": file1["id"]})
        pydrive_retry(file2.FetchContent)
        self.assertEqual(file2.GetContentString(), "")

        self.DeleteUploadedFiles(drive, [file1["id"]])

    # Tests for Trash/UnTrash/Delete.
    # ===============================

    def test_Files_Trash_File(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        self.assertFalse(file1.metadata[u"labels"][u"trashed"])

        # Download to verify non-trashed state on GDrive.
        file2 = drive.CreateFile({"id": file1["id"]})
        pydrive_retry(file2.FetchMetadata)
        self.assertFalse(file2.metadata[u"labels"][u"trashed"])

        pydrive_retry(file1.Trash)
        self.assertTrue(file1.metadata[u"labels"][u"trashed"])

        pydrive_retry(file2.FetchMetadata)
        self.assertTrue(file2.metadata[u"labels"][u"trashed"])

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_Files_Trash_File_Just_ID(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        self.assertFalse(file1.metadata[u"labels"][u"trashed"])

        # Trash file by ID.
        file2 = drive.CreateFile({"id": file1["id"]})
        pydrive_retry(file2.Trash)

        # Verify trashed by downloading metadata.
        pydrive_retry(file1.FetchMetadata)
        self.assertTrue(file1.metadata[u"labels"][u"trashed"])

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_Files_UnTrash_File(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        pydrive_retry(file1.Trash)
        self.assertTrue(file1.metadata[u"labels"][u"trashed"])

        # Verify that file is trashed by downloading metadata.
        file2 = drive.CreateFile({"id": file1["id"]})
        pydrive_retry(file2.FetchMetadata)
        self.assertTrue(file2.metadata[u"labels"][u"trashed"])

        # Un-trash the file, and assert local metadata is updated correctly.
        pydrive_retry(file1.UnTrash)
        self.assertFalse(file1.metadata[u"labels"][u"trashed"])

        # Re-fetch the metadata, and assert file un-trashed on GDrive.
        pydrive_retry(file2.FetchMetadata)
        self.assertFalse(file2.metadata[u"labels"][u"trashed"])

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_Files_UnTrash_File_Just_ID(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        pydrive_retry(file1.Trash)
        self.assertTrue(file1.metadata[u"labels"][u"trashed"])

        file2 = drive.CreateFile({"id": file1["id"]})
        pydrive_retry(file2.UnTrash)  # UnTrash without fetching metadata.

        pydrive_retry(file1.FetchMetadata)
        self.assertFalse(file1.metadata[u"labels"][u"trashed"])

        self.DeleteUploadedFiles(drive, [file1["id"]])

    def test_Files_Delete_File(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        file2 = drive.CreateFile({"id": file1["id"]})

        pydrive_retry(file1.Delete)

        try:
            pydrive_retry(file2.FetchMetadata)
            self.fail("File not deleted correctly.")
        except ApiRequestError:
            pass

    def test_Files_Delete_File_Just_ID(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        file2 = drive.CreateFile({"id": file1["id"]})

        pydrive_retry(file2.Delete)

        try:
            pydrive_retry(file1.FetchMetadata)
            self.fail("File not deleted correctly.")
        except ApiRequestError:
            pass

    # Tests for Permissions.
    # ======================

    def test_Files_FetchMetadata_Fields(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)

        self.assertFalse("permissions" in file1)

        pydrive_retry(file1.FetchMetadata, "permissions")
        self.assertTrue("permissions" in file1)
        pydrive_retry(file1.Delete)

    def test_Files_FetchAllMetadata_Fields(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)

        pydrive_retry(file1.FetchMetadata, fetch_all=True)
        self.assertTrue("hasThumbnail" in file1)
        self.assertTrue("thumbnailVersion" in file1)
        self.assertTrue("permissions" in file1)
        pydrive_retry(file1.Delete)

    def test_Files_Insert_Permission(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)

        # Verify only one permission before inserting permission.
        permissions = pydrive_retry(file1.GetPermissions)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(len(file1["permissions"]), 1)

        # Insert the permission.
        permission = pydrive_retry(
            file1.InsertPermission,
            {"type": "anyone", "value": "anyone", "role": "reader"},
        )
        self.assertTrue(permission)
        self.assertEqual(len(file1["permissions"]), 2)
        self.assertEqual(file1["permissions"][0]["type"], "anyone")

        permissions = pydrive_retry(file1.GetPermissions)
        self.assertEqual(len(file1["permissions"]), 2)
        self.assertEqual(file1["permissions"][0]["type"], "anyone")
        self.assertEqual(permissions[0]["type"], "anyone")

        # Verify remote changes made.
        file2 = drive.CreateFile({"id": file1["id"]})
        permissions = pydrive_retry(file2.GetPermissions)
        self.assertEqual(len(permissions), 2)
        self.assertEqual(permissions[0]["type"], "anyone")

        pydrive_retry(file1.Delete)

    def test_Files_Get_Permissions(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)

        self.assertFalse("permissions" in file1)

        permissions = pydrive_retry(file1.GetPermissions)
        self.assertTrue(permissions is not None)
        self.assertTrue("permissions" in file1)

        pydrive_retry(file1.Delete)

    def test_Files_Delete_Permission(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)
        pydrive_retry(
            file1.InsertPermission,
            {"type": "anyone", "value": "anyone", "role": "reader"},
        )
        permissions = pydrive_retry(file1.GetPermissions)
        self.assertEqual(len(permissions), 2)
        self.assertEqual(len(file1["permissions"]), 2)

        pydrive_retry(file1.DeletePermission, permissions[0]["id"])
        self.assertEqual(len(file1["permissions"]), 1)

        # Verify remote changes made.
        file2 = drive.CreateFile({"id": file1["id"]})
        permissions = pydrive_retry(file2.GetPermissions)
        self.assertEqual(len(permissions), 1)

        pydrive_retry(file1.Delete)

    def test_Files_Delete_Permission_Invalid(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()
        pydrive_retry(file1.Upload)

        try:
            pydrive_retry(file1.DeletePermission, "invalid id")
            self.fail("Deleting invalid permission not raising exception.")
        except ApiRequestError:
            pass

        pydrive_retry(file1.Delete)

    def test_ApiRequestError_HttpError_Propagation(self):
        file = GoogleDrive(self.ga).CreateFile()
        pydrive_retry(file.Upload)
        try:
            pydrive_retry(file.DeletePermission, "invalid id")
            self.fail("Deleting invalid permission not raising exception.")
        except ApiRequestError as exc:
            self.assertTrue(
                exc.args and isinstance(exc.args[0], errors.HttpError)
            )
            self.assertTrue(exc.error is not None)
            # Validating for HttpError 404 "Permission not found: invalid id"
            self.assertTrue(exc.error["code"] == 404)
        finally:
            pydrive_retry(file.Delete)

    def test_GFile_Conversion_Lossless_String(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()

        # Upload a string, and convert into Google Doc format.
        test_string = "Generic, non-exhaustive ASCII test string."
        file1.SetContentString(test_string)
        pydrive_retry(file1.Upload, {"convert": True})

        # Download string as plain text.
        downloaded_string = file1.GetContentString(mimetype="text/plain")
        self.assertEqual(
            test_string, downloaded_string, "Strings do not match"
        )

        # Download content into file and ensure that file content matches original
        # content string.
        downloaded_file_name = "_tmp_downloaded_file_name.txt"
        pydrive_retry(
            file1.GetContentFile,
            downloaded_file_name,
            mimetype="text/plain",
            remove_bom=True,
        )
        downloaded_string = open(downloaded_file_name).read()
        self.assertEqual(
            test_string, downloaded_string, "Strings do not match"
        )

        # Delete temp file.
        delete_file(downloaded_file_name)

    # Tests for GDrive conversion.
    # ============================

    def setup_gfile_conversion_test(self):
        drive = GoogleDrive(self.ga)
        file1 = drive.CreateFile()

        # Create a file to upload.
        file_name = "_tmp_source_file.txt"
        downloaded_file_name = "_tmp_downloaded_file_name.txt"
        original_file_content = "Generic, non-exhaustive\n ASCII test string."
        source_file = open(file_name, mode="w+")
        source_file.write(original_file_content)
        source_file.close()
        original_file_content = test_util.StripNewlines(original_file_content)

        return file1, file_name, original_file_content, downloaded_file_name

    def cleanup_gfile_conversion_test(
        self, file1, file_name, downloaded_file_name
    ):
        # Delete temporary files.
        os.path.exists(file_name) and os.remove(file_name)
        os.path.exists(downloaded_file_name) and os.remove(
            downloaded_file_name
        )
        pydrive_retry(file1.Delete)  # Delete uploaded file.

    def test_GFile_Conversion_Remove_BOM(self):
        (
            file1,
            file_name,
            original_file_content,
            downloaded_file_name,
        ) = self.setup_gfile_conversion_test()
        try:
            # Upload source_file and convert into Google Doc format.
            file1.SetContentFile(file_name)
            pydrive_retry(file1.Upload, {"convert": True})

            # Download as string.
            downloaded_content_no_bom = file1.GetContentString(
                mimetype="text/plain", remove_bom=True
            )
            downloaded_content_no_bom = test_util.StripNewlines(
                downloaded_content_no_bom
            )
            self.assertEqual(original_file_content, downloaded_content_no_bom)

            # Download as file.
            pydrive_retry(
                file1.GetContentFile, downloaded_file_name, remove_bom=True
            )
            downloaded_content = open(downloaded_file_name).read()
            downloaded_content = test_util.StripNewlines(downloaded_content)
            self.assertEqual(original_file_content, downloaded_content)

        finally:
            self.cleanup_gfile_conversion_test(
                file1, file_name, downloaded_file_name
            )

    def test_Gfile_Conversion_Add_Remove_BOM(self):
        """Tests whether you can switch between the BOM appended and removed
    version on the fly."""
        (
            file1,
            file_name,
            original_file_content,
            downloaded_file_name,
        ) = self.setup_gfile_conversion_test()
        try:
            file1.SetContentFile(file_name)
            pydrive_retry(file1.Upload, {"convert": True})

            content_bom = file1.GetContentString(mimetype="text/plain")
            content_no_bom = file1.GetContentString(
                mimetype="text/plain", remove_bom=True
            )
            content_bom_2 = file1.GetContentString(mimetype="text/plain")

            self.assertEqual(content_bom, content_bom_2)
            self.assertNotEqual(content_bom, content_no_bom)
            self.assertTrue(len(content_bom) > len(content_no_bom))

            buffer_bom = pydrive_retry(
                file1.GetContentIOBuffer,
                mimetype="text/plain",
                encoding="utf-8",
            )
            buffer_bom = u"".join(iter(buffer_bom))
            self.assertEqual(content_bom, buffer_bom)

            buffer_no_bom = pydrive_retry(
                file1.GetContentIOBuffer,
                mimetype="text/plain",
                remove_bom=True,
                encoding="utf-8",
            )
            buffer_no_bom = u"".join(iter(buffer_no_bom))
            self.assertEqual(content_no_bom, buffer_no_bom)

        finally:
            self.cleanup_gfile_conversion_test(
                file1, file_name, downloaded_file_name
            )

    def test_InsertPrefix(self):
        # Create BytesIO.
        file_obj = BytesIO("abc".encode("utf8"))
        original_length = len(file_obj.getvalue())
        char_to_insert = u"\ufeff".encode("utf8")

        # Insert the prefix.
        GoogleDriveFile._InsertPrefix(file_obj, char_to_insert)
        modified_length = len(file_obj.getvalue())
        self.assertGreater(modified_length, original_length)
        self.assertEqual(file_obj.getvalue(), u"\ufeffabc".encode("utf8"))

    def test_InsertPrefixLarge(self):
        # Create BytesIO.
        test_content = "abc" * 800
        file_obj = BytesIO(test_content.encode("utf-8"))
        original_length = len(file_obj.getvalue())
        char_to_insert = u"\ufeff".encode("utf8")

        # Insert the prefix.
        GoogleDriveFile._InsertPrefix(file_obj, char_to_insert)
        modified_length = len(file_obj.getvalue())
        self.assertGreater(modified_length, original_length)
        expected_content = u"\ufeff" + test_content
        self.assertEqual(file_obj.getvalue(), expected_content.encode("utf8"))

    def test_RemovePrefix(self):
        # Create BytesIO.
        file_obj = BytesIO(u"\ufeffabc".encode("utf8"))
        original_length = len(file_obj.getvalue())
        char_to_remove = u"\ufeff".encode("utf8")

        # Insert the prefix.
        GoogleDriveFile._RemovePrefix(file_obj, char_to_remove)
        modified_length = len(file_obj.getvalue())
        self.assertLess(modified_length, original_length)
        self.assertEqual(file_obj.getvalue(), "abc".encode("utf8"))

    def test_RemovePrefixLarge(self):
        # Create BytesIO.
        test_content = u"\ufeff" + u"abc" * 800
        file_obj = BytesIO(test_content.encode("utf8"))
        original_length = len(file_obj.getvalue())
        char_to_remove = u"\ufeff".encode("utf8")

        # Insert the prefix.
        GoogleDriveFile._RemovePrefix(file_obj, char_to_remove)
        modified_length = len(file_obj.getvalue())
        self.assertLess(modified_length, original_length)
        self.assertEqual(file_obj.getvalue(), test_content[1:].encode("utf8"))

    # Setup for concurrent upload testing.
    # =====================================
    FILE_UPLOAD_COUNT = 10

    def _parallel_uploader(self, num_of_uploads, num_of_workers):
        """
        :returns: list[str] of file IDs
        """
        drive = GoogleDrive(self.ga)
        thread_pool = ThreadPoolExecutor(max_workers=num_of_workers)
        first_file = self.getTempFile("first_file", "some string")
        second_file = self.getTempFile("second_file", "another string")

        # Create list of gdrive_files.
        upload_files = []
        remote_name = test_util.CreateRandomFileName()
        for i in range(num_of_uploads):
            file_name = first_file if i % 2 == 0 else second_file
            up_file = drive.CreateFile()
            up_file["title"] = remote_name
            up_file.SetContentFile(file_name)
            upload_files.append(up_file)

        # Ensure there are no files with the random file name.
        files = pydrive_retry(
            lambda: drive.ListFile(
                param={"q": "title = '%s' and trashed = false" % remote_name}
            ).GetList()
        )
        self.assertTrue(len(files) == 0)

        # Submit upload jobs to ThreadPoolExecutor.
        futures = []
        for up_file in upload_files:
            futures.append(thread_pool.submit(pydrive_retry, up_file.Upload))

        # Ensure that all threads a) return, and b) encountered no exceptions.
        for future in as_completed(futures):
            self.assertIsNone(future.exception())
        thread_pool.shutdown()

        # Ensure all files were uploaded.
        files = pydrive_retry(
            lambda: drive.ListFile(
                param={"q": "title = '%s' and trashed = false" % remote_name}
            ).GetList()
        )
        self.assertTrue(len(files) == self.FILE_UPLOAD_COUNT)

        return [fi["id"] for fi in upload_files]

    def _parallel_downloader(self, file_ids, num_of_workers):
        drive = GoogleDrive(self.ga)
        thread_pool = ThreadPoolExecutor(max_workers=num_of_workers)

        # Create list of gdrive_files.
        download_files = []
        for file_id in file_ids:
            file1 = drive.CreateFile({"id": file_id})
            file1["title"] = self.getTempFile()
            download_files.append(file1)

        # Ensure files don't exist yet.
        for file_obj in download_files:
            self.assertTrue(not delete_file(file_obj["title"]))

        # Submit upload jobs to ThreadPoolExecutor.
        futures = []
        for file_obj in download_files:
            futures.append(
                thread_pool.submit(
                    pydrive_retry, file_obj.GetContentFile, file_obj["title"]
                )
            )

        # Ensure that all threads a) return, and b) encountered no exceptions.
        for future in as_completed(futures):
            self.assertIsNone(future.exception())
        thread_pool.shutdown()

        # Ensure all files were downloaded.
        for file_obj in download_files:
            self.assertTrue(delete_file(file_obj["title"]))

        # Remove uploaded files.
        self.DeleteUploadedFiles(drive, file_ids)

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="timeout_decorator doesn't support Windows",
    )
    @timeout_decorator.timeout(320)
    def test_Parallel_Insert_File_Passed_HTTP(self):
        files = self._parallel_uploader(self.FILE_UPLOAD_COUNT, 10)
        self._parallel_downloader(files, 10)

    # Helper functions.
    # =================

    def DeleteUploadedFiles(self, drive, ids):
        for element in ids:
            tmp_file = drive.CreateFile({"id": element})
            pydrive_retry(tmp_file.Delete)


if __name__ == "__main__":
    unittest.main()
