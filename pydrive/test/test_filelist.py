# -*- coding: utf-8 -*-
import os
import sys
import unittest

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveFileListTest(unittest.TestCase):
  """Tests operations of files.GoogleDriveFileList class.
  Equivalent to Files.list in Google Drive API.
  """

  title = 'asdfjoijawioejgoiaweoganoqpnmgzwrouihoaiwe.ioawejogiawoj'
  ga = GoogleAuth('settings/test1.yaml')
  ga.LocalWebserverAuth()
  drive = GoogleDrive(ga)
  file_list = []
  for x in range(0, 10):
    file1 = drive.CreateFile()
    file1['title'] = title
    file1.Upload()
    file_list.append(file1)

  def test_01_Files_List_GetList(self):
    drive = GoogleDrive(self.ga)
    flist = drive.ListFile({'q': "title = '%s' and trashed = false"%self.title})
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

  def DeleteOldFile(self, file_name):
    try:
      os.remove(file_name)
    except OSError:
      pass

if __name__ == '__main__':
  unittest.main()
