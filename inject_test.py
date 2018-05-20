from common import inject


class Feature1(object):

  def run(self):
    print 'feature 1'


class Feature2A(object):

  def run(self):
    print 'feature 2(a)'


class Feature2B(object):

  def run(self):
    print 'feature 2(b)'


class User(object):

  def __init__(self):
    self._feature2 = inject.Feature('Feature2')

  @property
  @inject.feature('Feature1')
  def feature1(self):
    pass

  def run(self):
    self.feature1.run()
    self._feature2.run()


broker = inject.FeatureBroker.get_instance()
broker.provide('Feature1', Feature1())
broker.provide('Feature2', Feature2B())

user = User()
user.run()