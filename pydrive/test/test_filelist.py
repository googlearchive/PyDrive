# -*- coding: utf-8 -*-
import os
import sys
import unittest

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.test import test_util


class GoogleDriveFileListTest(unittest.TestCase):
  """Tests operations of files.GoogleDriveFileList class.
  Equivalent to Files.list in Google Drive API.
  """
  ga = GoogleAuth('settings/test1.yaml')
  ga.LocalWebserverAuth()
  drive = GoogleDrive(ga)

  def test_01_Files_List_GetList(self):
    drive = GoogleDrive(self.ga)
    flist = drive.ListFile({'q': "title = '%s' and trashed = false"
                                 % self.title})
    files = flist.GetList()  # Auto iterate every file
    for file1 in self.file_list:
      found = False
      for file2 in files:
        if file1['id'] == file2['id']:
          found = True
      self.assertEqual(found, True)

  def test_02_Files_List_ForLoop(self):
    drive = GoogleDrive(self.ga)
    flist = drive.ListFile({'q': "title = '%s' and trashed = false"%self.title,
                            'maxResults': 2})
    files = []
    for x in flist:  # Build iterator to access files simply with for loop
      self.assertTrue(len(x) <= 2)
      files.extend(x)
    for file1 in self.file_list:
      found = False
      for file2 in files:
        if file1['id'] == file2['id']:
          found = True
      self.assertEqual(found, True)

  def test_03_Files_List_GetList_Iterate(self):
    drive = GoogleDrive(self.ga)
    flist = drive.ListFile({'q': "title = '%s' and trashed = false"%self.title,
                            'maxResults': 2})
    files = []
    while True:
      try:
        x = flist.GetList()
        self.assertTrue(len(x) <= 2)
        files.extend(x)
      except StopIteration:
        break
    for file1 in self.file_list:
      found = False
      for file2 in files:
        if file1['id'] == file2['id']:
          found = True
      self.assertEqual(found, True)

  def test_File_List_Folders(self):
    drive = GoogleDrive(self.ga)
    folder1 = drive.CreateFile(
      {'mimeType': 'application/vnd.google-apps.folder',
       'title': self.title})
    folder1.Upload()
    self.file_list.append(folder1)

    flist = drive.ListFile({'q': "title = '%s' and trashed = false"
                                 % self.title})
    count = 0
    for _flist in flist:
      for file1 in _flist:
        self.assertFileInFileList(file1)
        count += 1

    self.assertTrue(count == 11)

  # setUp and tearDown methods.
  # ===========================
  def setUp(self):
    title = test_util.CreateRandomFileName()
    file_list = []
    for x in range(0, 10):
      file1 = self.drive.CreateFile()
      file1['title'] = title
      file1.Upload()
      file_list.append(file1)

    self.title = title
    self.file_list = file_list

  def tearDown(self):
    # Deleting uploaded files.
    for file1 in self.file_list:
      file1.Delete()

  def assertFileInFileList(self, file_object):
    found = False
    for file1 in self.file_list:
      if file_object['id'] == file1['id']:
        found = True
    self.assertEqual(found, True)

  def DeleteOldFile(self, file_name):
    try:
      os.remove(file_name)
    except OSError:
      pass

if __name__ == '__main__':
  unittest.main()
