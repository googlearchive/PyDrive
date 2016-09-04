Quickstart
=============================

Authentication
--------------
Drive API requires OAuth2.0 for authentication. *PyDrive* makes your life much easier by handling complex authentication steps for you.

1. Go to `APIs Console`_ and make your own project.
2. Search for 'Google Drive API', select the entry, and click 'Enable'.
3. Select 'Credentials' from the left menu, click 'Create Credentials', select 'OAuth client ID'.
4. Now, the product name and consent screen need to be set -> click 'Configure consent screen' and follow the instructions. Once finished:

 a. Select 'Application type' to be *Web application*.
 b. Enter an appropriate name.
 c. Input *http://localhost:8080* for 'Authorized JavaScript origins'.
 d. Input *http://localhost:8080/* for 'Authorized redirect URIs'.
 e. Click 'Create'.

5. Click 'Download JSON' on the right side of Client ID to download **client_secret_<really long ID>.json**.

The downloaded file has all authentication information of your application.
**Rename the file to "client_secrets.json" and place it in your working directory.**

Create *quickstart.py* file and copy and paste the following code.

.. code-block:: python

    from pydrive.auth import GoogleAuth

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

Run this code with *python quickstart.py* and you will see a web browser asking you for authentication. Click *Accept* and you are done with authentication. For more details, take a look at documentation: `OAuth made easy`_

.. _`APIs Console`: https://console.developers.google.com/iam-admin/projects
.. _`OAuth made easy`: ./oauth.html

Creating and updating file
--------------------------

There are many methods to create and update file metadata and contents. With *PyDrive*, all you have to know is `Upload()`_ method which makes optimal API call for you. Add the following code to your *quickstart.py* and run it.

.. code-block:: python

    from pydrive.drive import GoogleDrive

    drive = GoogleDrive(gauth)

    file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1.SetContentString('Hello World!') # Set content of the file from given string.
    file1.Upload()

This code will create a new file with title *Hello.txt* and its content *Hello World!*. You can see and open this file from `Google Drive`_ if you want. For more details, take a look at documentation: `File management made easy`_

.. _`Upload()`: ./pydrive.html#pydrive.files.GoogleDriveFile.Upload
.. _`Google Drive`: https://drive.google.com
.. _`File management made easy`: ./filemanagement.html

Getting list of files
---------------------

*PyDrive* handles paginations and parses response as list of `GoogleDriveFile`_. Let's get title and id of all the files in the root folder of Google Drive. Again, add the following code to *quickstart.py* and execute it.

.. code-block:: python

    # Auto-iterate through all files that matches this query
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
      print('title: %s, id: %s' % (file1['title'], file1['id']))

You will see title and id of all the files and folders in root folder of your Google Drive. For more details, take a look at documentation: `File listing made easy`_

.. _`GoogleDriveFile`: ./pydrive.html#pydrive.files.GoogleDriveFile
.. _`File listing made easy`: ./filelist.html
