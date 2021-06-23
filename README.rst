Deprecated
----------

This project is deprecated and no longer maintained. No further changes will be made.

In one of the PyDrive `issues <https://github.com/googleworkspace/PyDrive/issues/199>`_, we learned about the `PyDrive2 <https://github.com/iterative/PyDrive2>`_ fork of PyDrive. Forks are permitted under PyDrive's `license <LICENSE>`_, and we hope that such forks will be useful for the needs of PyDrive users. The PyDrive team makes no endorsement or support promises of any particular fork, but we're excited to see the open source license being a vehicle for new project development.


PyDrive
-------

*PyDrive* is a wrapper library of
`google-api-python-client <https://github.com/google/google-api-python-client>`_
that simplifies many common Google Drive API tasks.

Project Info
------------

- Homepage: `https://pypi.python.org/pypi/PyDrive <https://pypi.python.org/pypi/PyDrive>`_
- Documentation: `Official documentation on GitHub pages <https://googleworkspace.github.io/PyDrive/docs/build/html/index.html>`_
- GitHub: `https://github.com/googleworkspace/PyDrive <https://github.com/googleworkspace/PyDrive>`_

Features of PyDrive
-------------------

-  Simplifies OAuth2.0 into just few lines with flexible settings.
-  Wraps `Google Drive API <https://developers.google.com/drive/>`_ into
   classes of each resource to make your program more object-oriented.
-  Helps common operations else than API calls, such as content fetching
   and pagination control.

How to install
--------------

You can install PyDrive with regular ``pip`` command.

::

    $ pip install PyDrive

To install the current development version from GitHub, use:

::

    $  pip install git+https://github.com/googleworkspace/PyDrive.git#egg=PyDrive

OAuth made easy
---------------

Download *client\_secrets.json* from Google API Console and OAuth2.0 is
done in two lines. You can customize behavior of OAuth2 in one settings
file *settings.yaml*.

.. code:: python


    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

File management made easy
-------------------------

Upload/update the file with one method. PyDrive will do it in the most
efficient way.

.. code:: python

    file1 = drive.CreateFile({'title': 'Hello.txt'})
    file1.SetContentString('Hello')
    file1.Upload() # Files.insert()

    file1['title'] = 'HelloWorld.txt'  # Change title of the file
    file1.Upload() # Files.patch()

    content = file1.GetContentString()  # 'Hello'
    file1.SetContentString(content+' World!')  # 'Hello World!'
    file1.Upload() # Files.update()

    file2 = drive.CreateFile()
    file2.SetContentFile('hello.png')
    file2.Upload()
    print('Created file %s with mimeType %s' % (file2['title'],
    file2['mimeType']))
    # Created file hello.png with mimeType image/png

    file3 = drive.CreateFile({'id': file2['id']})
    print('Downloading file %s from Google Drive' % file3['title']) # 'hello.png'
    file3.GetContentFile('world.png')  # Save Drive file as a local file

    # or download Google Docs files in an export format provided.
    # downloading a docs document as an html file:
    docsfile.GetContentFile('test.html', mimetype='text/html')

File listing pagination made easy
---------------------------------

*PyDrive* handles file listing pagination for you.

.. code:: python

    # Auto-iterate through all files that matches this query
    file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
    for file1 in file_list:
        print('title: {}, id: {}'.format(file1['title'], file1['id']))

    # Paginate file lists by specifying number of max results
    for file_list in drive.ListFile({'maxResults': 10}):
        print('Received {} files from Files.list()'.format(len(file_list))) # <= 10
        for file1 in file_list:
            print('title: {}, id: {}'.format(file1['title'], file1['id']))

Concurrent access made easy
---------------------------

All calls made are thread-safe. The underlying implementation in the
google-api-client library
`is not thread-safe <https://developers.google.com/api-client-library/python/guide/thread_safety>`_,
which means that every request has to re-authenticate an http object. You
can avoid this overhead by
creating your own http object for each thread and re-use it for every call.

This can be done as follows:

.. code:: python

    # Create httplib.Http() object.
    http = drive.auth.Get_Http_Object()

    # Create file object to upload.
    file_obj = drive.CreateFile()
    file_obj['title'] = "file name"

    # Upload the file and pass the http object into the call to Upload.
    file_obj.Upload(param={"http": http})

You can specify the http-object in every access method which takes a *param*
parameter.

Note: This is  not an official Google product.
