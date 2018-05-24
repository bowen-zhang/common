from common import pattern


class _Feature(object):
  def __init__(self, feature_name, feature_provider, feature_singleton, *args,
               **kwargs):
    self._name = feature_name
    self._provider = feature_provider
    self._singleton = feature_singleton
    self._args = args
    self._kwargs = kwargs
    self._feature = None

  def create(self):
    if self._singleton:
      if not self._feature:
        self._feature = self._create()
      return self._feature
    else:
      return self._create()

  def _create(self):
    if callable(self._provider):
      return self._provider(*self._args, **self._kwargs)
    else:
      return self._provider


class FeatureBrokerException(Exception):
  pass


class FeatureBroker(pattern.Singleton):
  def __init__(self, *args, **kwargs):
    super(FeatureBroker, self).__init__(*args, **kwargs)
    self._features = {}

  def provide(self, feature_name, feature_provider, *args, **kwargs):
    feature = _Feature(
        feature_name,
        feature_provider,
        feature_singleton=False,
        *args,
        **kwargs)
    self._features[feature_name] = feature

  def provide_one(self, feature_name, feature_provider, *args, **kwargs):
    feature = _Feature(
        feature_name,
        feature_provider,
        feature_singleton=True,
        *args,
        **kwargs)
    self._features[feature_name] = feature

  def require(self, feature_name, lazy_creation=True):
    if lazy_creation:
      return _FeatureStub(self, feature_name)
    else:
      return self[feature_name]

  def __getitem__(self, feature_name):
    if feature_name not in self._features:
      raise FeatureBrokerException(
          'No provider for feature "{0}".'.format(feature_name))

    feature = self._features[feature_name]
    return feature.create()


class _FeatureStub(object):
  def __init__(self, broker, name):
    self._broker = broker
    self._name = name
    self._instance = None

  def __get__(self, obj, T):
    if not self._instance:
      self._instance = self._broker[self._name]
    return self._instance

  def __getattr__(self, name):
    if not self._instance:
      self._instance = self._broker[self._name]
    return getattr(self._instance, name)


def feature(name):
  def outter_wrapper(f):
    def inner_wrapper(self, *args):
      if not hasattr(self, '_feature_instances'):
        self._feature_instances = {}
      if name not in self._feature_instances:
        self._feature_instances[name] = FeatureBroker.get_instance()[name]
      return self._feature_instances[name]

    return inner_wrapper

  return outter_wrapper
