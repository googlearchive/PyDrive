Quickstart
=============================

Authentication
--------------
Drive API requires OAuth2.0 for authentication. *PyDrive2* makes your life much easier by handling complex authentication steps for you.

1. Go to `APIs Console`_ and make your own project.
2. Search for 'Google Drive API', select the entry, and click 'Enable'.
3. Select 'Credentials' from the left menu, click 'Create Credentials', select 'OAuth client ID'.
4. Now, the product name and consent screen need to be set -> click 'Configure consent screen' and follow the instructions. Once finished:

 a. Select 'Application type' to be *Web application*.
 b. Enter an appropriate name.
 c. Input *http://localhost:8080/* for 'Authorized redirect URIs'.
 d. Click 'Create'.

5. Click 'Download JSON' on the right side of Client ID to download **client_secret_<really long ID>.json**.

The downloaded file has all authentication information of your application.
**Rename the file to "client_secrets.json" and place it in your working directory.**

Create *quickstart.py* file and copy and paste the following code.

.. code-block:: python

    from pydrive2.auth import GoogleAuth

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

Run this code with *python quickstart.py* and you will see a web browser asking you for authentication. Click *Accept* and you are done with authentication. For more details, take a look at documentation: `OAuth made easy`_

.. _`APIs Console`: https://console.developers.google.com/iam-admin/projects
.. _`OAuth made easy`: ./oauth.html

Creating and Updating Files
---------------------------

There are many methods to create and update file metadata and contents. With *PyDrive2*, all you have to know is
`Upload()`_ method which makes optimal API call for you. Add the following code to your *quickstart.py* and run it.

.. code-block:: python

    from pydrive2.drive import GoogleDrive

    drive = GoogleDrive(gauth)

    file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1.SetContentString('Hello World!') # Set content of the file from given string.
    file1.Upload()

This code will create a new file with title *Hello.txt* and its content *Hello World!*. You can see and open this
 file from `Google Drive`_ if you want. For more details, take a look at documentation: `File management made easy`_

.. _`Upload()`: ./pydrive2.html#pydrive2.files.GoogleDriveFile.Upload
.. _`Google Drive`: https://drive.google.com
.. _`File management made easy`: ./filemanagement.html

Listing Files
-------------

*PyDrive2* handles paginations and parses response as list of `GoogleDriveFile`_. Let's get title and id of all the files in the root folder of Google Drive. Again, add the following code to *quickstart.py* and execute it.

.. code-block:: python

    # Auto-iterate through all files that matches this query
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
      print('title: %s, id: %s' % (file1['title'], file1['id']))

Creating a Folder
-----------------

GoogleDrive treats everything as a file and assigns different mimetypes for different file formats. A folder is thus
 also a file with a special mimetype. The code below allows you to add a subfolder to an existing folder.

.. code-block:: python

    def create_folder(parent_folder_id, subfolder_name):
      newFolder = drive.CreateFile({'title': subfolder_name, "parents": [{"kind": "drive#fileLink", "id": \
      parent_folder_id}],"mimeType": "application/vnd.google-apps.folder"})
      newFolder.Upload()
      return newFolder


Return File ID via File Title
-----------------------------

A common task is providing the Google Drive API with a file id.
``get_id_of_title`` demonstrates a simple workflow to return the id of a file handle by searching the file titles in a
given directory. The function takes two arguments, ``title`` and ``parent_directory_id``. ``title`` is a string that
will be compared against file titles included in a directory identified by the ``parent_directory_id``.

.. code-block:: python

    def get_id_of_title(title,parent_directory_id):
      foldered_list=drive.ListFile({'q':  "'"+parent_directory_id+"' in parents and trashed=false"}).GetList()
      for file in foldered_list:
        if(file['title']==title):
          return file['id']
        return None

Browse Folders
--------------
This returns a json output of the data in a directory with some important attributes like size, title, parent_id.

.. code-block:: python

    browsed=[]
    def folder_browser(folder_list,parent_id):
      for element in folder_list:
        if type(element) is dict:
          print (element['title'])
        else:
          print (element)
      print("Enter Name of Folder You Want to Use\nEnter '/' to use current folder\nEnter ':' to create New Folder and
      use that" )
      inp=input()
      if inp=='/':
        return parent_id
      elif inp==':':
        print("Enter Name of Folder You Want to Create")
        inp=input()
        newfolder=create_folder(parent_id,inp)
        if not os.path.exists(HOME_DIRECTORY+ROOT_FOLDER_NAME+os.path.sep+USERNAME):
          os.makedirs(HOME_DIRECTORY+ROOT_FOLDER_NAME+os.path.sep+USERNAME)
        return newfolder['id']

      else:
        folder_selected=inp
        for element in folder_list:
          if type(element) is dict:
            if element["title"]==folder_selected:
              struc=element["list"]
              browsed.append(folder_selected)
              print("Inside "+folder_selected)
              return folder_browser(struc,element['id'])

here ``folder_list`` is the list of folders that is present

You will see title and id of all the files and folders in root folder of your Google Drive. For more details, refer to the documentation: `File listing made easy`_

.. _`GoogleDriveFile`: ./pydrive2.html#pydrive2.files.GoogleDriveFile
.. _`File listing made easy`: ./filelist.html
