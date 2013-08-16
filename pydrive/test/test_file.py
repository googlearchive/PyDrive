# -*- coding: utf-8 -*-
import filecmp
import os
import sys
import unittest

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveFileTest(unittest.TestCase):
  """Tests basic file operations of files.GoogleDriveFile.
  Mainly upload and download of contents and metadata.
  Equivalent to Files.insert, Files.update, Files.patch in Google Drive API.
  """

  ga = GoogleAuth('settings/test1.yaml')
  ga.LocalWebserverAuth()
  first_file = 'a.png'
  second_file = 'b.png'

  def test_01_Files_Insert(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'firsttestfile'
    file1['title'] = filename
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    file2 = drive.CreateFile({'id': file1['id']})  # Download file from id
    self.assertEqual(file2['title'], filename)

  def test_02_Files_Insert_Unicode(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = u'첫번째 파일'
    file1['title'] = filename
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    file2 = drive.CreateFile({'id': file1['id']})  # Download file from id
    self.assertEqual(file2['title'], filename)

  def test_03_Files_Insert_Content_String(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'secondtestfile'
    content = 'hello world!'
    file1['title'] = filename
    file1.SetContentString(content)
    file1.Upload()  # Files.insert
    self.assertEqual(file1.GetContentString(), content)
    file1.FetchContent()  # Force download and double check content
    self.assertEqual(file1.metadata['title'], filename)
    self.assertEqual(file1.GetContentString(), content)
    file2 = drive.CreateFile({'id': file1['id']})  # Download file from id
    self.assertEqual(file2.GetContentString(), content)
    self.assertEqual(file2.metadata['title'], filename)

  def test_04_Files_Insert_Content_Unicode_String(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = u'두번째 파일'
    content = u'안녕 세상아!'
    file1['title'] = filename
    file1.SetContentString(content)
    file1.Upload()  # Files.insert
    self.assertEqual(file1.GetContentString(), content)
    self.assertEqual(file1.metadata['title'], filename)
    file1.FetchContent()  # Force download and double check content
    self.assertEqual(file1.GetContentString(), content)
    file2 = drive.CreateFile({'id': file1['id']})  # Download file from id
    self.assertEqual(file2.GetContentString(), content)
    self.assertEqual(file2.metadata['title'], filename)

  def test_05_Files_Insert_Content_File(self):
    self.DeleteOldFile(self.first_file+'1')
    self.DeleteOldFile(self.first_file+'2')
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'filecontent'
    file1['title'] = filename
    file1.SetContentFile(self.first_file)
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    file1.FetchContent()  # Force download and double check content
    file1.GetContentFile(self.first_file+'1')
    self.assertEqual(filecmp.cmp(self.first_file, self.first_file+'1'), True)
    file2 = drive.CreateFile({'id': file1['id']})  # Download file from id
    file2.GetContentFile(self.first_file+'2')
    self.assertEqual(filecmp.cmp(self.first_file, self.first_file+'2'), True)

  def test_06_Files_Patch(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'prepatchtestfile'
    newfilename = 'patchtestfile'
    file1['title'] = filename
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    file1['title'] = newfilename
    file1.Upload()  # Files.patch
    self.assertEqual(file1.metadata['title'], newfilename)
    file2 = drive.CreateFile({'id': file1['id']})  # Download file from id
    file2.FetchMetadata()
    self.assertEqual(file2.metadata['title'], newfilename)

  def test_07_Files_Patch_Skipping_Content(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'prepatchtestfile'
    newfilename = 'patchtestfile'
    content = 'hello world!'
    file1['title'] = filename
    file1.SetContentString(content)
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    file1['title'] = newfilename
    file1.Upload()  # Files.patch
    self.assertEqual(file1.metadata['title'], newfilename)
    self.assertEqual(file1.GetContentString(), content)
    self.assertEqual(file1.GetContentString(), content)

  def test_08_Files_Update_String(self):
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'preupdatetestfile'
    newfilename = 'updatetestfile'
    content = 'hello world!'
    newcontent = 'hello new world!'
    file1['title'] = filename
    file1.SetContentString(content)
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    self.assertEqual(file1.GetContentString(), content)
    file1.FetchContent()  # Force download and double check content
    self.assertEqual(file1.GetContentString(), content)
    file1['title'] = newfilename
    file1.SetContentString(newcontent)
    file1.Upload()  # Files.update
    self.assertEqual(file1.metadata['title'], newfilename)
    self.assertEqual(file1.GetContentString(), newcontent)
    self.assertEqual(file1.GetContentString(), newcontent)

  def test_09_Files_Update_File(self):
    self.DeleteOldFile(self.first_file+'1')
    self.DeleteOldFile(self.second_file+'1')
    drive = GoogleDrive(self.ga)
    file1 = drive.CreateFile()
    filename = 'preupdatetestfile'
    newfilename = 'updatetestfile'
    file1['title'] = filename
    file1.SetContentFile(self.first_file)
    file1.Upload()  # Files.insert
    self.assertEqual(file1.metadata['title'], filename)
    file1.FetchContent()  # Force download and double check content
    file1.GetContentFile(self.first_file+'1')
    self.assertEqual(filecmp.cmp(self.first_file, self.first_file+'1'), True)
    file1['title'] = newfilename
    file1.SetContentFile(self.second_file)
    file1.Upload()  # Files.update
    self.assertEqual(file1.metadata['title'], newfilename)
    file1.GetContentFile(self.second_file+'1')
    self.assertEqual(filecmp.cmp(self.second_file, self.second_file+'1'), True)

  def DeleteOldFile(self, file_name):
    try:
      os.remove(file_name)
    except OSError:
      pass

if __name__ == '__main__':
  unittest.main()
