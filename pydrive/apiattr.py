class ApiAttribute(object):
  """A data descriptor that sets and returns values."""

  def __init__(self, name):
    """Create an instance of ApiAttribute.

    :param name: name of this attribute.
    :type name: str.
    """
    self.name = name

  def __get__(self, obj, type=None):
    """Accesses value of this attribute."""
    return obj.attr.get(self.name)

  def __set__(self, obj, value):
    """Write value of this attribute."""
    obj.attr[self.name] = value
    if obj.dirty.get(self.name) is not None:
      obj.dirty[self.name] = True

  def __del__(self, obj):
    """Delete value of this attribute."""
    del obj.attr[self.name]
    if obj.dirty.get(self.name) is not None:
      del obj.dirty[self.name]


class ApiAttributeMixin(object):
  """Mixin to initialize required global variables to use ApiAttribute."""

  def __init__(self):
    self.attr = {}
    self.dirty = {}


class ApiResource(dict):
  """Super class of all api resources.

  Inherits and behaves as a python dictionary to handle api resources.
  Save clean copy of metadata in self.metadata as a dictionary.
  Provides changed metadata elements to efficiently update api resources.
  """
  auth = ApiAttribute('auth')

  def __init__(self, *args, **kwargs):
    """Create an instance of ApiResource."""
    self.update(*args, **kwargs)

  def __getitem__(self, key):
    """Overwritten method of dictionary.

    :param key: key of the query.
    :type key: str.
    :returns: value of the query.
    """
    return dict.__getitem__(self, key)

  def __setitem__(self, key, val):
    """Overwritten method of dictionary.

    :param key: key of the query.
    :type key: str.
    :param val: value of the query.
    """
    dict.__setitem__(self, key, val)

  def __repr__(self):
    """Overwritten method of dictionary."""
    dictrepr = dict.__repr__(self)
    return '%s(%s)' % (type(self).__name__, dictrepr)

  def update(self, *args, **kwargs):
    """Overwritten method of dictionary."""
    for k, v in dict(*args, **kwargs).iteritems():
      self[k] = v

  def UpdateMetadata(self, metadata=None):
    """Update metadata and mark all of them to be clean."""
    if metadata:
      self.update(metadata)
    self.metadata = dict(self)

  def GetChanges(self):
    """Returns changed metadata elements to update api resources efficiently.

    :returns: dict -- changed metadata elements.
    """
    dirty = {}
    for key in self:
      if self.metadata.get(key) is None:
        dirty[key] = self[key]
      elif self.metadata[key] != self[key]:
        dirty[key] = self[key]
    return dirty


class ApiResourceList(ApiAttributeMixin, ApiResource):
  """Abstract class of all api list resources.

  Inherits ApiResource and builds iterator to list any API resource.
  """
  metadata = ApiAttribute('metadata')

  def __init__(self, auth=None, metadata=None):
    """Create an instance of ApiResourceList.

    :param auth: authorized GoogleAuth instance.
    :type auth: GoogleAuth.
    :param metadata: parameter to send to list command.
    :type metadata: dict.
    """
    ApiAttributeMixin.__init__(self)
    ApiResource.__init__(self)
    self.auth = auth
    self.UpdateMetadata()
    if metadata:
      self.update(metadata)

  def __iter__(self):
    """Returns iterator object.

    :returns: ApiResourceList -- self
    """
    return self

  def next(self):
    """Make API call to list resources and return them.

    Auto updates 'pageToken' everytime it makes API call and
    raises StopIteration when it reached the end of iteration.

    :returns: list -- list of API resources.
    :raises: StopIteration
    """
    if 'pageToken' in self and self['pageToken'] is None:
      raise StopIteration
    result = self._GetList()
    self['pageToken'] = self.metadata.get('nextPageToken')
    return result

  def GetList(self):
    """Get list of API resources.

    If 'maxResults' is not specified, it will automatically iterate through
    every resources available. Otherwise, it will make API call once and
    update 'pageToken'.

    :returns: list -- list of API resources.
    """
    if self.get('maxResults') is None:
      self['maxResults'] = 1000
      result = []
      for x in self:
        result.extend(x)
      del self['maxResults']
      return result
    else:
      return self.next()

  def _GetList(self):
    """Helper function which actually makes API call.

    Should be overwritten.

    :raises: NotImplementedError
    """
    raise NotImplementedError

  def Reset(self):
    """Resets current iteration"""
    if 'pageToken' in self:
      del self['pageToken']
