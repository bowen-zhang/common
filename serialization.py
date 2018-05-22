import abc


class Serializer(object):

  @classmethod
  def uuid(cls):
    return hash(cls.__module__ + '.' + cls.__name__)

  def serialize(self):
    """Serializes current object instance to binary string.

    Returns:
      A string containing binary data.
    """
    pass

  @classmethod
  def deserialize(cls, bin_str):
    """Deserializes from binary string to object instance.

    Args:
      bin_str: a string containing binary data.
    Returns:
      Object instance.
    """
    pass
