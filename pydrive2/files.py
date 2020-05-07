import io
import mimetypes
import json

from googleapiclient import errors
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from functools import wraps

from .apiattr import ApiAttribute
from .apiattr import ApiAttributeMixin
from .apiattr import ApiResource
from .apiattr import ApiResourceList
from .auth import LoadAuth

BLOCK_SIZE = 1024
# Usage: MIME_TYPE_TO_BOM['<Google Drive mime type>']['<download mimetype>'].
MIME_TYPE_TO_BOM = {
    "application/vnd.google-apps.document": {
        "text/plain": u"\ufeff".encode("utf8")
    }
}


class FileNotUploadedError(RuntimeError):
    """Error trying to access metadata of file that is not uploaded."""


class ApiRequestError(IOError):
    def __init__(self, http_error):
        assert isinstance(http_error, errors.HttpError)
        content = json.loads(http_error.content.decode("utf-8"))
        self.error = content.get("error", {}) if content else {}

        # Initialize args for backward compatibility
        super().__init__(http_error)

    def GetField(self, field):
        """Returns the `field` from the first error"""
        return self.error.get("errors", [{}])[0].get(field, "")


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

    :returns: list -- list of pydrive2.files.GoogleDriveFile.
    """
        # Teamdrive support
        self["supportsAllDrives"] = True
        self["includeItemsFromAllDrives"] = True

        try:
            self.metadata = (
                self.auth.service.files()
                .list(**dict(self))
                .execute(http=self.http)
            )
        except errors.HttpError as error:
            raise ApiRequestError(error)

        result = []
        for file_metadata in self.metadata["items"]:
            tmp_file = GoogleDriveFile(
                auth=self.auth, metadata=file_metadata, uploaded=True
            )
            result.append(tmp_file)
        return result


class GoogleDriveFile(ApiAttributeMixin, ApiResource):
    """Google Drive File instance.

  Inherits ApiResource which inherits dict.
  Can access and modify metadata like dictionary.
  """

    content = ApiAttribute("content")
    uploaded = ApiAttribute("uploaded")
    metadata = ApiAttribute("metadata")

    def __init__(self, auth=None, metadata=None, uploaded=False):
        """Create an instance of GoogleDriveFile.

    :param auth: authorized GoogleAuth instance.
    :type auth: pydrive2.auth.GoogleAuth
    :param metadata: file resource to initialize GoogleDriveFile with.
    :type metadata: dict.
    :param uploaded: True if this file is confirmed to be uploaded.
    :type uploaded: bool.
    """
        ApiAttributeMixin.__init__(self)
        ApiResource.__init__(self)
        self.metadata = {}
        self.dirty = {"content": False}
        self.auth = auth
        self.uploaded = uploaded
        if uploaded:
            self.UpdateMetadata(metadata)
        elif metadata:
            self.update(metadata)
        self._ALL_FIELDS = (
            "alternateLink,appDataContents,"
            "canComment,canReadRevisions,"
            "copyable,createdDate,defaultOpenWithLink,description,"
            "downloadUrl,editable,embedLink,etag,explicitlyTrashed,"
            "exportLinks,fileExtension,fileSize,folderColorRgb,"
            "fullFileExtension,headRevisionId,iconLink,id,"
            "imageMediaMetadata,indexableText,isAppAuthorized,kind,"
            "labels,lastModifyingUser,lastModifyingUserName,"
            "lastViewedByMeDate,markedViewedByMeDate,md5Checksum,"
            "mimeType,modifiedByMeDate,modifiedDate,openWithLinks,"
            "originalFilename,ownedByMe,ownerNames,owners,parents,"
            "permissions,properties,quotaBytesUsed,selfLink,shareable,"
            "shared,sharedWithMeDate,sharingUser,spaces,thumbnail,"
            "thumbnailLink,title,userPermission,version,"
            "videoMediaMetadata,webContentLink,webViewLink,writersCanShare"
        )
        self.has_bom = True

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
        except KeyError as e:
            if self.uploaded:
                raise KeyError(e)
            if self.get("id"):
                self.FetchMetadata()
                return dict.__getitem__(self, key)
            else:
                raise FileNotUploadedError()

    def SetContentString(self, content, encoding="utf-8"):
        """Set content of this file to be a string.

    Creates io.BytesIO instance of utf-8 encoded string.
    Sets mimeType to be 'text/plain' if not specified.

    :param encoding: The encoding to use when setting the content of this file.
    :type encoding: str
    :param content: content of the file in string.
    :type content: str
    """
        self.content = io.BytesIO(content.encode(encoding))
        if self.get("mimeType") is None:
            self["mimeType"] = "text/plain"

    def SetContentFile(self, filename):
        """Set content of this file from a file.

    Opens the file specified by this method.
    Will be read, uploaded, and closed by Upload() method.
    Sets metadata 'title' and 'mimeType' automatically if not specified.

    :param filename: name of the file to be uploaded.
    :type filename: str.
    """
        self.content = open(filename, "rb")
        if self.get("title") is None:
            self["title"] = filename
        if self.get("mimeType") is None:
            self["mimeType"] = mimetypes.guess_type(filename)[0]

    def GetContentString(
        self, mimetype=None, encoding="utf-8", remove_bom=False
    ):
        """Get content of this file as a string.

    :param mimetype: The mimetype of the content string.
    :type mimetype: str

    :param encoding: The encoding to use when decoding the byte string.
    :type encoding: str

    :param remove_bom: Whether to strip a known BOM.
    :type remove_bom: bool

    :returns: str -- utf-8 decoded content of the file
    :raises: ApiRequestError, FileNotUploadedError, FileNotDownloadableError
    """
        if (
            self.content is None
            or type(self.content) is not io.BytesIO
            or self.has_bom == remove_bom
        ):
            self.FetchContent(mimetype, remove_bom)
        return self.content.getvalue().decode(encoding)

    @LoadAuth
    def GetContentFile(
        self, filename, mimetype=None, remove_bom=False, callback=None
    ):
        """Save content of this file as a local file.

    :param filename: name of the file to write to.
    :type filename: str
    :param mimetype: mimeType of the file.
    :type mimetype: str
    :param remove_bom: Whether to remove the byte order marking.
    :type remove_bom: bool
    :param callback: passed two arguments: (total trasferred, file size).
    :type param: callable
    :raises: ApiRequestError, FileNotUploadedError
    """
        files = self.auth.service.files()
        file_id = self.metadata.get("id") or self.get("id")
        if not file_id:
            raise FileNotUploadedError()

        def download(fd, request):
            # Ensures thread safety. Similar to other places where we call
            # `.execute(http=self.http)` to pass a client from the thread
            # local storage.
            if self.http:
                request.http = self.http
            downloader = MediaIoBaseDownload(fd, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if callback:
                    callback(status.resumable_progress, status.total_size)

        with open(filename, mode="w+b") as fd:
            # Ideally would use files.export_media instead if
            # metadata.get("mimeType").startswith("application/vnd.google-apps.")
            # but that would first require a slow call to FetchMetadata()
            try:
                download(fd, files.get_media(fileId=file_id))
            except errors.HttpError as error:
                exc = ApiRequestError(error)
                if (
                    exc.error["code"] != 403
                    or exc.GetField("reason") != "fileNotDownloadable"
                ):
                    raise exc
                mimetype = mimetype or "text/plain"
                fd.seek(0)  # just in case `download()` modified `fd`
                try:
                    download(
                        fd,
                        files.export_media(fileId=file_id, mimeType=mimetype),
                    )
                except errors.HttpError as error:
                    raise ApiRequestError(error)

            if mimetype == "text/plain" and remove_bom:
                fd.seek(0)
                boms = [
                    bom[mimetype]
                    for bom in MIME_TYPE_TO_BOM.values()
                    if mimetype in bom
                ]
                if boms:
                    self._RemovePrefix(fd, boms[0])

    @LoadAuth
    def FetchMetadata(self, fields=None, fetch_all=False):
        """Download file's metadata from id using Files.get().

    :param fields: The fields to include, as one string, each entry separated
    by commas, e.g. 'fields,labels'.
    :type fields: str

    :param fetch_all: Whether to fetch all fields.
    :type fetch_all: bool

    :raises: ApiRequestError, FileNotUploadedError
    """
        file_id = self.metadata.get("id") or self.get("id")

        if fetch_all:
            fields = self._ALL_FIELDS

        if file_id:
            try:
                metadata = (
                    self.auth.service.files()
                    .get(
                        fileId=file_id,
                        fields=fields,
                        # Teamdrive support
                        supportsAllDrives=True,
                    )
                    .execute(http=self.http)
                )
            except errors.HttpError as error:
                raise ApiRequestError(error)
            else:
                self.uploaded = True
                self.UpdateMetadata(metadata)
        else:
            raise FileNotUploadedError()

    @LoadMetadata
    def FetchContent(self, mimetype=None, remove_bom=False):
        """Download file's content from download_url.

    :raises: ApiRequestError, FileNotUploadedError, FileNotDownloadableError
    """
        download_url = self.metadata.get("downloadUrl")
        export_links = self.metadata.get("exportLinks")
        if download_url:
            self.content = io.BytesIO(self._DownloadFromUrl(download_url))
            self.dirty["content"] = False

        elif export_links and export_links.get(mimetype):
            self.content = io.BytesIO(
                self._DownloadFromUrl(export_links.get(mimetype))
            )
            self.dirty["content"] = False

        else:
            raise FileNotDownloadableError(
                "No downloadLink/exportLinks for mimetype found in metadata"
            )

        if mimetype == "text/plain" and remove_bom:
            self._RemovePrefix(
                self.content, MIME_TYPE_TO_BOM[self["mimeType"]][mimetype]
            )
            self.has_bom = not remove_bom

    def Upload(self, param=None):
        """Upload/update file by choosing the most efficient method.

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError
    """
        if self.uploaded or self.get("id") is not None:
            if self.dirty["content"]:
                self._FilesUpdate(param=param)
            else:
                self._FilesPatch(param=param)
        else:
            self._FilesInsert(param=param)

    def Trash(self, param=None):
        """Move a file to the trash.

    :raises: ApiRequestError
    """
        self._FilesTrash(param=param)

    def UnTrash(self, param=None):
        """Move a file out of the trash.
    :param param: Additional parameter to file.
    :type param: dict.
    :raises: ApiRequestError
    """
        self._FilesUnTrash(param=param)

    def Delete(self, param=None):
        """Hard-delete a file.

    :param param: additional parameter to file.
    :type param: dict.
    :raises: ApiRequestError
    """
        self._FilesDelete(param=param)

    def InsertPermission(self, new_permission):
        """Insert a new permission. Re-fetches all permissions after call.

    :param new_permission: The new permission to insert, please see the
    official Google Drive API guide on permissions.insert for details.

    :type new_permission: object

    :return: The permission object.
    :rtype: object
    """
        file_id = self.metadata.get("id") or self["id"]
        try:
            permission = (
                self.auth.service.permissions()
                .insert(fileId=file_id, body=new_permission)
                .execute(http=self.http)
            )
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            self.GetPermissions()  # Update permissions field.

        return permission

    @LoadAuth
    def GetPermissions(self):
        """Downloads all permissions from Google Drive, as this information is
    not downloaded by FetchMetadata by default.

    :return: A list of the permission objects.
    :rtype: object[]
    """
        self.FetchMetadata(fields="permissions")
        return self.metadata.get("permissions")

    def DeletePermission(self, permission_id):
        """Deletes the permission specified by the permission_id.

    :param permission_id: The permission id.
    :type permission_id: str
    :return: True if it succeeds.
    :rtype: bool
    """
        return self._DeletePermission(permission_id)

    @LoadAuth
    def _FilesInsert(self, param=None):
        """Upload a new file using Files.insert().

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError
    """
        if param is None:
            param = {}
        param["body"] = self.GetChanges()

        # teamdrive support
        param["supportsAllDrives"] = True

        try:
            if self.dirty["content"]:
                param["media_body"] = self._BuildMediaBody()
            metadata = (
                self.auth.service.files()
                .insert(**param)
                .execute(http=self.http)
            )
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            self.uploaded = True
            self.dirty["content"] = False
            self.UpdateMetadata(metadata)

    @LoadAuth
    def _FilesUnTrash(self, param=None):
        """Un-delete (Trash) a file using Files.UnTrash().
    :param param: additional parameter to file.
    :type param: dict.
    :raises: ApiRequestError
    """
        if param is None:
            param = {}
        param["fileId"] = self.metadata.get("id") or self["id"]

        # Teamdrive support
        param["supportsAllDrives"] = True

        try:
            self.auth.service.files().untrash(**param).execute(http=self.http)
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            if self.metadata:
                self.metadata[u"labels"][u"trashed"] = False
            return True

    @LoadAuth
    def _FilesTrash(self, param=None):
        """Soft-delete (Trash) a file using Files.Trash().

    :param param: additional parameter to file.
    :type param: dict.
    :raises: ApiRequestError
    """
        if param is None:
            param = {}
        param["fileId"] = self.metadata.get("id") or self["id"]

        # Teamdrive support
        param["supportsAllDrives"] = True

        try:
            self.auth.service.files().trash(**param).execute(http=self.http)
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            if self.metadata:
                self.metadata[u"labels"][u"trashed"] = True
            return True

    @LoadAuth
    def _FilesDelete(self, param=None):
        """Delete a file using Files.Delete()
    (WARNING: deleting permanently deletes the file!)

    :param param: additional parameter to file.
    :type param: dict.
    :raises: ApiRequestError
    """
        if param is None:
            param = {}
        param["fileId"] = self.metadata.get("id") or self["id"]

        # Teamdrive support
        param["supportsAllDrives"] = True

        try:
            self.auth.service.files().delete(**param).execute(http=self.http)
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            return True

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
        param["body"] = self.GetChanges()
        param["fileId"] = self.metadata.get("id")

        # Teamdrive support
        param["supportsAllDrives"] = True

        try:
            if self.dirty["content"]:
                param["media_body"] = self._BuildMediaBody()
            metadata = (
                self.auth.service.files()
                .update(**param)
                .execute(http=self.http)
            )
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            self.uploaded = True
            self.dirty["content"] = False
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
        param["body"] = self.GetChanges()
        param["fileId"] = self.metadata.get("id")

        # Teamdrive support
        param["supportsAllDrives"] = True

        try:
            metadata = (
                self.auth.service.files()
                .patch(**param)
                .execute(http=self.http)
            )
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            self.UpdateMetadata(metadata)

    def _BuildMediaBody(self):
        """Build MediaIoBaseUpload to get prepared to upload content of the file.

    Sets mimeType as 'application/octet-stream' if not specified.

    :returns: MediaIoBaseUpload -- instance that will be used to upload content.
    """
        if self.get("mimeType") is None:
            self["mimeType"] = "application/octet-stream"
        return MediaIoBaseUpload(
            self.content, self["mimeType"], resumable=True
        )

    @LoadAuth
    def _DownloadFromUrl(self, url):
        """Download file from url using provided credential.

    :param url: link of the file to download.
    :type url: str.
    :returns: str -- content of downloaded file in string.
    :raises: ApiRequestError
    """
        resp, content = self.http.request(url)
        if resp.status != 200:
            raise ApiRequestError(errors.HttpError(resp, content, uri=url))
        return content

    @LoadAuth
    def _DeletePermission(self, permission_id):
        """Deletes the permission remotely, and from the file object itself.

    :param permission_id: The ID of the permission.
    :type permission_id: str

    :return: The permission
    :rtype: object
    """
        file_id = self.metadata.get("id") or self["id"]
        try:
            self.auth.service.permissions().delete(
                fileId=file_id, permissionId=permission_id
            ).execute()
        except errors.HttpError as error:
            raise ApiRequestError(error)
        else:
            if "permissions" in self and "permissions" in self.metadata:
                permissions = self["permissions"]
                is_not_current_permission = (
                    lambda per: per["id"] == permission_id
                )
                permissions = list(
                    filter(is_not_current_permission, permissions)
                )
                self["permissions"] = permissions
                self.metadata["permissions"] = permissions
            return True

    @staticmethod
    def _RemovePrefix(file_object, prefix, block_size=BLOCK_SIZE):
        """Deletes passed prefix by shifting content of passed file object by to
    the left. Operation is in-place.

    Args:
      file_object (obj): The file object to manipulate.
      prefix (str): The prefix to insert.
      block_size (int): The size of the blocks which are moved one at a time.
    """
        prefix_length = len(prefix)
        # Detect if prefix exists in file.
        content_start = file_object.read(prefix_length)

        if content_start == prefix:
            # Shift content left by prefix length, by copying 1KiB at a time.
            block_to_write = file_object.read(block_size)
            current_block_length = len(block_to_write)

            # Read and write location in separate variables for simplicity.
            read_location = prefix_length + current_block_length
            write_location = 0

            while current_block_length > 0:
                # Write next block.
                file_object.seek(write_location)
                file_object.write(block_to_write)
                # Set write location to the next block.
                write_location += len(block_to_write)

                # Read next block of input.
                file_object.seek(read_location)
                block_to_write = file_object.read(block_size)
                # Update the current block length and read_location.
                current_block_length = len(block_to_write)
                read_location += current_block_length

            # Truncate the file to its, now shorter, length.
            file_object.truncate(read_location - prefix_length)

    @staticmethod
    def _InsertPrefix(file_object, prefix, block_size=BLOCK_SIZE):
        """Inserts the passed prefix in the beginning of the file, operation is
    in-place.

    Args:
      file_object (obj): The file object to manipulate.
      prefix (str): The prefix to insert.
    """
        # Read the first two blocks.
        first_block = file_object.read(block_size)
        second_block = file_object.read(block_size)
        # Pointer to the first byte of the next block to be read.
        read_location = block_size * 2

        # Write BOM.
        file_object.seek(0)
        file_object.write(prefix)
        # {read|write}_location separated for readability.
        write_location = len(prefix)

        # Write and read block alternatingly.
        while len(first_block):
            # Write first block.
            file_object.seek(write_location)
            file_object.write(first_block)
            # Increment write_location.
            write_location += block_size

            # Move second block into first variable.
            first_block = second_block

            # Read in the next block.
            file_object.seek(read_location)
            second_block = file_object.read(block_size)
            # Increment read_location.
            read_location += block_size
