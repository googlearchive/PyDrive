.. image:: https://travis-ci.com/iterative/pydrive2.svg?branch=master
  :target: https://travis-ci.com/iterative/pydrive2
  :alt: Travis

PyDrive2
--------

*PyDrive2* is a wrapper library of
`google-api-python-client <https://github.com/google/google-api-python-client>`_
that simplifies many common Google Drive API tasks. It is an actively
maintained fork of `https://pypi.python.org/pypi/PyDrive <https://pypi.python.org/pypi/PyDrive>`_.
By the authors and maintainers of the `Git for Data <https://dvc.org>`_ - DVC
project.

Project Info
------------

- Homepage: `https://pypi.python.org/pypi/PyDrive2 <https://pypi.python.org/pypi/PyDrive2>`_
- Documentation: `Official documentation on GitHub pages <https://iterative.github.io/PyDrive2/docs/build/html/index.html>`_
- GitHub: `https://github.com/iterative/PyDrive2 <https://github.com/iterative/PyDrive2>`_
- `Running tests </pydrive2/test/README.rst>`_

Features of PyDrive2
--------------------

-  Simplifies OAuth2.0 into just few lines with flexible settings.
-  Wraps `Google Drive API <https://developers.google.com/drive/>`_ into
   classes of each resource to make your program more object-oriented.
-  Helps common operations else than API calls, such as content fetching
   and pagination control.

How to install
--------------

You can install PyDrive2 with regular ``pip`` command.

::

    $ pip install PyDrive2

To install the current development version from GitHub, use:

::

    $  pip install git+https://github.com/iterative/PyDrive2.git#egg=PyDrive2

OAuth made easy
---------------

Download *client\_secrets.json* from Google API Console and OAuth2.0 is
done in two lines. You can customize behavior of OAuth2 in one settings
file *settings.yaml*.

.. code:: python


    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

File management made easy
-------------------------

Upload/update the file with one method. PyDrive2 will do it in the most
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

*PyDrive2* handles file listing pagination for you.

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

All API functions made to be thread-safe.
