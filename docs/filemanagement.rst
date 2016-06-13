File management made easy
=========================

There are many methods to create and update file metadata and contents. With *PyDrive*, you don't have to care about any of these different API methods. Manipulate file metadata and contents from `GoogleDriveFile`_ object and call `Upload()`_. *PyDrive* will make optimal API call for you.

Upload a new file
-----------------

Here is a sample code to upload a file. ``gauth`` is an authenticated `GoogleAuth`_ object.

::

    from pydrive.drive import GoogleDrive

    drive = GoogleDrive(gauth) # Create GoogleDrive instance with authenticated GoogleAuth instance

    file1 = drive.CreateFile({'title': 'Hello.txt'}) # Create GoogleDriveFile instance with title 'Hello.txt'
    file1.Upload() # Upload it
    print 'title: %s, id: %s' % (file1['title'], file1['id']) # title: Hello.txt, id: {{FILE_ID}}

Now, you will have a file 'Hello.txt' uploaded to your Google Drive. You can open it from web interface to check its content, 'Hello World!'.

Note that `CreateFile()`_ will create `GoogleDriveFile`_ instance but not actually upload a file to Google Drive. You can initialize `GoogleDriveFile`_ object by itself. However, it is not recommended to do so in order to keep authentication consistent.

Update file metadata
--------------------

You can manipulate file metadata from `GoogleDriveFile`_ object just as you manipulate ``dict``. Format of file metadata can be found from 
Google Drive API documentation: `Files resource`_

Sample code continues from above:

::

    file1['title'] = 'HelloWorld.txt' # Change title of the file
    file1.Upload() # Update metadata
    print 'title: %s' % file1['title'] # title: HelloWorld.txt

Now, the title of your file has changed to 'HelloWorld.txt'.

Download file metadata from file ID
-----------------------------------

You might want to get file metadata from file ID. In that case, just initialize `GoogleDriveFile`_ with file ID and access metadata from `GoogleDriveFile`_ just as you access ``dict``.

Sample code continues from above:

::

    file2 = drive.CreateFile({'id': file1['id']}) # Create GoogleDriveFile instance with file id of file1
    print 'title: %s, mimeType: %s' % (file2['title'], file2['mimeType']) # title: HelloWorld.txt, mimeType: text/plain

Upload and update file content
------------------------------

Managing file content is as easy as managing file metadata. You can set file content with either `SetContentFile(filename)`_ or `SetContentString(content)`_ and call `Upload()`_ just as you did to upload or update file metadata.

Sample code continues from above:

::

    file4 = drive.CreateFile({'title':'appdata.json', 'mimeType':'application/json'})
    file4.SetContentString('{"firstname": "John", "lastname": "Smith"}')
    file4.Upload() # Upload file
    file4.SetContentString('{"firstname": "Claudio", "lastname": "Afshar"}')
    file4.Upload() # Update content of the file

    file5 = drive.CreateFile()
    file5.SetContentFile('cat.png') # Read file and set it as a content of this instance.
    file5.Upload() # Upload it
    print 'title: %s, mimeType: %s' % (file5['title'], file5['mimeType']) # title: cat.png, mimeType: image/png

Download file content
---------------------

Just as you uploaded file content, you can download it using `GetContentFile(filename)`_ or `GetContentString()`_.

Sample code continues from above:

::

    file6 = drive.CreateFile({'id': file5['id']}) # Initialize GoogleDriveFile instance with file id
    file6.GetContentFile('catlove.png') # Download file as 'catlove.png'

    file7 = drive.CreateFile({'id': file4['id']}) # Initialize GoogleDriveFile instance with file id
    content = file7.GetContentString() # content: '{"firstname": "Claudio", "lastname": "Afshar"}'
    file7.SetContentString(content.replace('lastname', 'familyname'))
    file7.Upload() # Uploaded content: '{"firstname": "Claudio", "familyname": "Afshar"}'

.. _`GoogleDriveFile`: ./pydrive.html#pydrive.files.GoogleDriveFile
.. _`Upload()`: ./pydrive.html#pydrive.files.GoogleDriveFile.Upload
.. _`GoogleAuth`: ./pydrive.html#pydrive.auth.GoogleAuth
.. _`CreateFile()`: ./pydrive.html#pydrive.drive.GoogleDrive.CreateFile
.. _`Files resource`: https://developers.google.com/drive/v2/reference/files#resource
.. _`SetContentFile(filename)`: ./pydrive.html#pydrive.files.GoogleDriveFile.SetContentFile
.. _`SetContentString(content)`: ./pydrive.html#pydrive.files.GoogleDriveFile.SetContentString
.. _`GetContentFile(filename)`: ./pydrive.html#pydrive.files.GoogleDriveFile.GetContentFile
.. _`GetContentString()`: ./pydrive.html#pydrive.files.GoogleDriveFile.GetContentString
