from common import pattern


class FeatureBrokerException(Exception):
  pass


class FeatureBroker(pattern.Singleton):

  def __init__(self, *args, **kwargs):
    super(FeatureBroker, self).__init__(*args, **kwargs)
    self._providers = {}

  def provide(self, feature, provider, *args, **kwargs):
    if callable(provider):

      def call():
        return provider(*args, **kwargs)
    else:

      def call():
        return provider

    self._providers[feature] = call

  def __getitem__(self, feature):
    if feature not in self._providers:
      raise FeatureBrokerException(
          'No provider for feature "{0}".'.format(feature))

    provider = self._providers[feature]
    return provider()


class Feature(object):

  def __init__(self, name):
    self._name = name
    self._instance = None

  def __get__(self, obj, T):
    if not self._instance:
      self._instance = FeatureBroker.get_instance()[self._name]
    return self._instance

  def __getattr__(self, name):
    if not self._instance:
      self._instance = FeatureBroker.get_instance()[self._name]
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
