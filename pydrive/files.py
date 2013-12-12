import io
import mimetypes

from apiclient import errors
from apiclient.http import MediaIoBaseUpload
from functools import wraps

from .apiattr import ApiAttribute
from .apiattr import ApiAttributeMixin
from .apiattr import ApiResource
from .apiattr import ApiResourceList
from .auth import LoadAuth


class FileNotUploadedError(RuntimeError):
  """Error trying to access metadata of file that is not uploaded."""


class ApiRequestError(IOError):
  """Error while making any API requests."""


class FileNotDownloadableError(RuntimeError):
  """Error trying to download file that is not downloadable."""


def LoadMetadata(decoratee):
  """Decorator to check if the file has metadata and fetches it if not.

  :raises: ApiRequestError, FileNotUploadedError
  """
  @wraps(decoratee)
  def _decorated(self, *args, **kwargs):
    if not self.uploaded:
      self.FetchMetadata()
    return decoratee(self, *args, **kwargs)
  return _decorated


class GoogleDriveFileList(ApiResourceList):
  """Google Drive FileList instance.

  Equivalent to Files.list() in Drive APIs.
  """

  def __init__(self, auth=None, param=None):
    """Create an instance of GoogleDriveFileList."""
    super(GoogleDriveFileList, self).__init__(auth=auth, metadata=param)

  @LoadAuth
  def _GetList(self):
    """Overwritten method which actually makes API call to list files.

    :returns: list -- list of pydrive.files.GoogleDriveFile.
    """
    self.metadata = self.auth.service.files().list(**dict(self)).execute()
    result = []
    for file_metadata in self.metadata['items']:
      tmp_file = GoogleDriveFile(
          auth=self.auth,
          metadata=file_metadata,
          uploaded=True)
      result.append(tmp_file)
    return result


class GoogleDriveFile(ApiAttributeMixin, ApiResource):
  """Google Drive File instance.

  Inherits ApiResource which inherits dict.
  Can access and modify metadata like dictionary.
  """
  content = ApiAttribute('content')
  uploaded = ApiAttribute('uploaded')
  metadata = ApiAttribute('metadata')

  def __init__(self, auth=None, metadata=None, uploaded=False):
    """Create an instance of GoogleDriveFile.

    :param auth: authorized GoogleAuth instance.
    :type auth: pydrive.auth.GoogleAuth
    :param metadata: file resource to initialize GoogleDirveFile with.
    :type metadata: dict.
    :param uploaded: True if this file is confirmed to be uploaded.
    :type uploaded: bool.
    """
    ApiAttributeMixin.__init__(self)
    ApiResource.__init__(self)
    self.metadata = {}
    self.dirty = {'content': False}
    self.auth = auth
    self.uploaded = uploaded
    if uploaded:
      self.UpdateMetadata(metadata)
    elif metadata:
      self.update(metadata)

  def __getitem__(self, key):
    """Overwrites manner of accessing Files resource.

    If this file instance is not uploaded and id is specified,
    it will try to look for metadata with Files.get().

    :param key: key of dictionary query.
    :type key: str.
    :returns: value of Files resource
    :raises: KeyError, FileNotUploadedError
    """
    try:
      return dict.__getitem__(self, key)
    except KeyError, e:
      if self.uploaded:
        raise KeyError(e)
      if self.get('id'):
        self.FetchMetadata()
        return dict.__getitem__(self, key)
      else:
        raise FileNotUploadedError()

  def SetContentString(self, content):
    """Set content of this file to be a string.

    Creates io.BytesIO instance of utf-8 encoded string.
    Sets mimeType to be 'text/plain' if not specified.

    :param content: content of the file in string.
    :type content: str.
    """
    self.content = io.BytesIO(content.encode('utf-8'))
    if self.get('mimeType') is None:
      self['mimeType'] = 'text/plain'

  def SetContentFile(self, filename):
    """Set content of this file from a file.

    Opens the file specified by this method.
    Will be read, uploaded, and closed by Upload() method.
    Sets metadata 'title' and 'mimeType' automatically if not specified.

    :param filename: name of the file to be uploaded.
    :type filename: str.
    """
    self.content = open(filename, 'rb')
    if self.get('title') is None:
      self['title'] = filename
    if self.get('mimeType') is None:
      self['mimeType'] = mimetypes.guess_type(filename)[0]

  def GetContentString(self):
    """Get content of this file as a string.

    :returns: str -- utf-8 decoded content of the file
    :raises: ApiRequestError, FileNotUploadedError, FileNotDownloadableError
    """
    if self.content is None or type(self.content) is not io.BytesIO:
      self.FetchContent()
    return self.content.getvalue().decode('utf-8')

  def GetContentFile(self, filename, mimetype=None):
    """Save content of this file as a local file.

    :param filename: name of the file to write to.
    :type filename: str.
    :raises: ApiRequestError, FileNotUploadedError, FileNotDownloadableError
    """
    if self.content is None or type(self.content) is not io.BytesIO:
      self.FetchContent(mimetype)
    f = open(filename, 'wb')
    f.write(self.content.getvalue())
    f.close()

  @LoadAuth
  def FetchMetadata(self):
    """Download file's metadata from id using Files.get().

    :raises: ApiRequestError, FileNotUploadedError
    """
    file_id = self.metadata.get('id') or self.get('id')
    if file_id:
      try:
        metadata = self.auth.service.files().get(fileId=file_id).execute()
      except errors.HttpError, error:
        raise ApiRequestError(error)
      else:
        self.uploaded = True
        self.UpdateMetadata(metadata)
    else:
      raise FileNotUploadedError()

  @LoadMetadata
  def FetchContent(self, mimetype=None):
    """Download file's content from download_url.

    :raises: ApiRequestError, FileNotUploadedError, FileNotDownloadableError
    """
    download_url = self.metadata.get('downloadUrl')
    if download_url:
      self.content = io.BytesIO(self._DownloadFromUrl(download_url))
      self.dirty['content'] = False
      return
    
    export_links = self.metadata.get('exportLinks')
    if export_links and export_links.get(mimetype):
      self.content = io.BytesIO(
          self._DownloadFromUrl(export_links.get(mimetype)))
      self.dirty['content'] = False
      return

    raise FileNotDownloadableError(
        'No downloadLink/exportLinks for mimetype found in metadata')

  def Upload(self, param=None):
    """Upload/update file by choosing the most efficient method.

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError
    """
    if self.uploaded or self.get('id') is not None:
      if self.dirty['content']:
        self._FilesUpdate(param=param)
      else:
        self._FilesPatch(param=param)
    else:
      self._FilesInsert(param=param)

  @LoadAuth
  def _FilesInsert(self, param=None):
    """Upload a new file using Files.insert().

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError
    """
    if param is None:
      param = {}
    param['body'] = self.GetChanges()
    try:
      if self.dirty['content']:
        param['media_body'] = self._BuildMediaBody()
      metadata = self.auth.service.files().insert(**param).execute()
    except errors.HttpError, error:
      raise ApiRequestError(error)
    else:
      self.uploaded = True
      self.dirty['content'] = False
      self.UpdateMetadata(metadata)

  @LoadAuth
  @LoadMetadata
  def _FilesUpdate(self, param=None):
    """Update metadata and/or content using Files.Update().

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError, FileNotUploadedError
    """
    if param is None:
      param = {}
    param['body'] = self.GetChanges()
    param['fileId'] = self.metadata.get('id')
    try:
      if self.dirty['content']:
        param['media_body'] = self._BuildMediaBody()
      metadata = self.auth.service.files().update(**param).execute()
    except errors.HttpError, error:
      raise ApiRequestError(error)
    else:
      self.uploaded = True
      self.dirty['content'] = False
      self.UpdateMetadata(metadata)

  @LoadAuth
  @LoadMetadata
  def _FilesPatch(self, param=None):
    """Update metadata using Files.Patch().

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError, FileNotUploadedError
    """
    if param is None:
      param = {}
    param['body'] = self.GetChanges()
    param['fileId'] = self.metadata.get('id')
    try:
      metadata = self.auth.service.files().patch(**param).execute()
    except errors.HttpError, error:
      raise ApiRequestError(error)
    else:
      self.UpdateMetadata(metadata)

  def _BuildMediaBody(self):
    """Build MediaIoBaseUpload to get prepared to upload content of the file.

    Sets mimeType as 'application/octet-stream' if not specified.

    :returns: MediaIoBaseUpload -- instance that will be used to upload content.
    """
    if self.get('mimeType') is None:
      self['mimeType'] = 'application/octet-stream'
    return MediaIoBaseUpload(self.content, self['mimeType'])

  @LoadAuth
  def _DownloadFromUrl(self, url):
    """Download file from url using provided credential.

    :param url: link of the file to download.
    :type url: str.
    :returns: str -- content of downloaded file in string.
    :raises: ApiRequestError
    """
    resp, content = self.auth.service._http.request(url)
    if resp.status != 200:
      raise ApiRequestError('Cannot download file: %s' % resp)
    return content
