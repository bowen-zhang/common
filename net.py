import netifaces


class Interface(object):

  def __init__(self, name):
    self._name = name

  @classmethod
  def first(cls):
    interfaces = [x for x in netifaces.interfaces() if x != 'lo']
    if not interfaces:
      return None
    return Interface(interfaces[0])

  @property
  def ip(self):
    return self._get_address_by_type(netifaces.AF_INET)

  @property
  def mac_address(self):
    addr = self._get_address_by_type(netifaces.AF_LINK)
    return addr.replace(':', '') if addr else None

  def _get_address_by_type(self, addr_type):
    addr = netifaces.ifaddresses(self._name)
    if addr and addr_type in addr:
      addr = addr[addr_type]
      if addr and 'addr' in addr[0]:
        return addr[0]['addr']
    return None
