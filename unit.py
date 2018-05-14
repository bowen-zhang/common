"""Library of physical metrics to use with support of various unit conversions.

The following metrics are included:
  * Angle (radian, degree)
  * Length (meter, foot)
  * Duration (day, hour, minute, second, millisecond)
  * AngularSpeed (radian/sec, degree/sec)
  * Speed (meter/sec, foot/sec)
"""

import datetime
import math


class Angle(object):
  """Represents an angle for retrieval in radian or degree."""

  RADIAN = 1
  DEGREE = 2

  UNLIMITED_RANGE = None
  DEFAULT_RANGE = (0.0, 2 * math.pi)
  HEADING_RANGE = (0.0, 2 * math.pi)
  RELATIVE_RANGE = (-math.pi, math.pi)
  LONGITUDE_RANGE = (-math.pi, math.pi)
  LATITUDE_RANGE = (-math.pi / 2, math.pi / 2)

  _RADIAN_PER_DEGREE = math.pi / 180

  def __init__(self, value, unit, valid_range=DEFAULT_RANGE):
    """Create Angle object with angle value.

    Angle value will be shifted to specified range. So if range is -180 ~ +180,
    and value is 358, it will be shifted to -2.

    Args:
      value: angle value.
      unit: unit of angle (radian or degree)
      valid_range: range to shift angle value into.
    """
    if unit == Angle.DEGREE:
      value *= Angle._RADIAN_PER_DEGREE

    if valid_range:
      assert len(valid_range) == 2
      assert valid_range[0] < valid_range[1]
      r = valid_range
      if value < r[0]:
        self._value_rad = (value - r[0]) % (r[1] - r[0]) + r[0]
      elif value > r[1]:
        self._value_rad = (value - r[1]) % (r[0] - r[1]) + r[1]
      else:
        self._value_rad = value
    else:
      self._value_rad = value

  @property
  def radian(self):
    return self._value_rad

  @property
  def degree(self):
    return self._value_rad / Angle._RADIAN_PER_DEGREE

  def __str__(self):
    return '{0:.1f} degree'.format(self.degree)


class Length(object):
  """Represents a length for retrieval in meter or feet."""

  METER = 1
  FOOT = 2
  NAUTICAL_MILE = 3
  STATUTE_MILE = 4
  KILOMETER = 5

  _METER_PER_FOOT = 0.3048
  _METER_PER_NAUTICAL_MILE = 1852.0
  _METER_PER_STATUTE_MILE = 1609.34
  _METER_PER_KILOMETER = 1000

  def __init__(self, value=0, unit=METER):
    if unit == Length.FOOT:
      self._value_m = value * Length._METER_PER_FOOT
    elif unit == Length.NAUTICAL_MILE:
      self._value_m = value * Length._METER_PER_NAUTICAL_MILE
    elif unit == Length.STATUTE_MILE:
      self._value_m = value * Length._METER_PER_STATUTE_MILE
    elif unit == Length.KILOMETER:
      self._value_m = value * Length._METER_PER_KILOMETER
    else:
      self._value_m = float(value)

  @property
  def meter(self):
    return self._value_m

  @property
  def foot(self):
    return self._value_m / Length._METER_PER_FOOT

  @property
  def ft(self):
    return self.foot

  @property
  def nautical_mile(self):
    return self._value_m / Length._METER_PER_NAUTICAL_MILE

  @property
  def nm(self):
    return self.nautical_mile

  @property
  def statute_mile(self):
    return self._value_m / Length._METER_PER_STATUTE_MILE

  @property
  def sm(self):
    return self.statute_mile

  @property
  def kilometer(self):
    return self._value_m / Length._METER_PER_KILOMETER

  @property
  def km(self):
    return self.kilometer

  def __cmp__(self, other):
    if isinstance(other, Length):
      return cmp(self.meter, other.meter)
    else:
      return cmp(self.meter, other)

  def __str__(self):
    return '{0:.1f}ft'.format(self.ft)

  def __add__(self, other):
    assert isinstance(other, Length)
    return Length(self._value_m + other.meter, Length.METER)


class Geolocation(object):

  def __init__(self, longitude, latitude, elevation=0):
    self._longitude = longitude
    self._latitude = latitude
    self._elevation = elevation

  @property
  def longitude(self):
    return self._longitude

  @property
  def latitude(self):
    return self._latitude

  @property
  def elevation(self):
    return self._elevation

  def __sub__(self, other):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    assert isinstance(other, Geolocation)

    lon1 = self._longitude.radian
    lat1 = self._latitude.radian
    lon2 = other.longitude.radian
    lat2 = other.latitude.radian

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(
        dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return Length(c * r, Length.KILOMETER)

  def __str__(self):
    return '({0}, {1}) at {2}'.format(self.latitude, self.longitude,
                                      self.elevation)


class Duration(object):
  """Represents a duration for retrieval in day, hour, min, sec, msec."""

  MILLISECOND = 1
  SECOND = 2
  MINUTE = 3
  HOUR = 4
  DAY = 5

  _SECOND_PER_MILLISECOND = 0.001
  _SECOND_PER_MINUTE = 60
  _SECOND_PER_HOUR = 60 * 60
  _SECOND_PER_DAY = 24 * 60 * 60

  _EPOCH_MIN_DAY = datetime.datetime(1970, 1, 1)

  def __init__(self, value, unit):
    if unit == Duration.MILLISECOND:
      self._value_sec = value * Duration._SECOND_PER_MILLISECOND
    elif unit == Duration.MINUTE:
      self._value_sec = value * Duration._SECOND_PER_MINUTE
    elif unit == Duration.HOUR:
      self._value_sec = value * Duration._SECOND_PER_HOUR
    elif unit == Duration.DAY:
      self._value_sec = value * Duration._SECOND_PER_DAY
    else:
      self._value_sec = float(value)

  @property
  def millisecond(self):
    return self._value_sec / Duration._SECOND_PER_MILLISECOND

  @property
  def second(self):
    return self._value_sec

  @property
  def minute(self):
    return self._value_sec / Duration._SECOND_PER_MINUTE

  @property
  def hour(self):
    return self._value_sec / Duration._SECOND_PER_HOUR

  @property
  def day(self):
    return self._value_sec / Duration._SECOND_PER_DAY

  @property
  def time(self):
    x = int(self._value_sec)
    return datetime.time(x / 60 / 60 % 24, x % 3600 / 60, x % 60)

  def __cmp__(self, other):
    if isinstance(other, Duration):
      return cmp(self.second, other.second)
    else:
      return cmp(self.second, other)

  def __str__(self):
    return '{0:0>2}:{1:0>2}:{2:0>2}.{3:0>3}'.format(
        int(self.hour),
        int(self.minute) % 60,
        int(self.second) % 60, int(self.millisecond) % 1000)

  @staticmethod
  def from_epoch(datetime_obj):
    return Duration((datetime_obj - Duration._EPOCH_MIN_DAY).total_seconds(),
                    Duration.SECOND)


class AngularSpeed(object):
  """Represents an angular speed for retrieval in radian/sec or degree/sec."""

  def __init__(self, angle, duration):
    self._angle = angle
    self._duration = duration

  @property
  def radian_per_second(self):
    return self._angle.radian / self._duration.second

  @property
  def degree_per_second(self):
    return self._angle.degree / self._duration.second

  def __cmp__(self, other):
    if isinstance(other, AngularSpeed):
      return cmp(self.radian_per_second, other.radian_per_second)
    else:
      return cmp(self.radian_per_second, other)

  def __str__(self):
    return '{0:.1f}/second'.format(self.degree_per_second)


class Speed(object):
  """Represents a speed for retrieval in meter/sec or feet/sec."""

  def __init__(self, length, duration):
    self._length = length
    self._duration = duration

  @property
  def meter_per_second(self):
    return self._length.meter / self._duration.second

  @property
  def mps(self):
    return self._meter_per_second

  @property
  def foot_per_second(self):
    return self._length.foot / self._duration.second

  @property
  def fps(self):
    return self._foot_per_second

  @property
  def fpm(self):
    return self._length.foot / self._duration.minute

  @property
  def mph(self):
    return self._length.statute_mile / self._duration.hour

  @property
  def knots(self):
    return self._length.nautical_mile / self._duration.hour

  def __cmp__(self, other):
    if isinstance(other, Speed):
      return cmp(self.meter_per_second, other.meter_per_second)
    else:
      return cmp(self.meter_per_second, other)

  def __str__(self):
    return '{0}kts'.format(int(self.knots))


class Pressure(object):
  """Represents a pressure for retrieval in inHg/mmHg/Pa/hPa."""

  PA = 1
  HPA = 2
  INHG = 3
  MMHG = 4
  ATM = 5
  BAR = 6
  MILLIBAR = 7

  PA_PER_HPA = 100.0
  PA_PER_INHG = 3386.39
  PA_PER_MMHG = 133.32239
  PA_PER_ATM = 101325.0
  PA_PER_BAR = 100000.0
  PA_PER_MILLIBAR = 100.0

  def __init__(self, pressure, unit=PA):
    if unit == Pressure.PA:
      self._pressure = pressure
    elif unit == Pressure.HPA:
      self._pressure = pressure * Pressure.PA_PER_HPA
    elif unit == Pressure.INHG:
      self._pressure = pressure * Pressure.PA_PER_INHG
    elif unit == Pressure.MMHG:
      self._pressure = pressure * Pressure.PA_PER_MMHG
    elif unit == Pressure.ATM:
      self._pressure = pressure * Pressure.PA_PER_ATM
    elif unit == Pressure.BAR:
      self._pressure = pressure * Pressure.PA_PER_BAR
    elif unit == Pressure.MILLIBAR:
      self._pressure = pressure * Pressure.PA_PER_MILLIBAR
    else:
      assert False

  @property
  def pa(self):
    return self._pressure

  @property
  def hpa(self):
    return self._pressure / Pressure.PA_PER_HPA

  @property
  def inhg(self):
    return self._pressure / Pressure.PA_PER_INHG

  @property
  def mmhg(self):
    return self._pressure / Pressure.PA_PER_MMHG

  @property
  def atm(self):
    return self._pressure / Pressure.PA_PER_ATM

  @property
  def bar(self):
    return self._pressure / Pressure.PA_PER_BAR

  @property
  def millibar(self):
    return self._pressure / Pressure.PA_PER_MILLIBAR

  def __cmp__(self, other):
    if isinstance(other, Pressure):
      return cmp(self._pressure, other._pressure)
    else:
      return cmp(self._pressure, other)

  def __str__(self):
    return '{0:.2f}inHg'.format(self.inhg)


class Temperature(object):
  """Represents a temperature for retrieval in K/C/F."""

  KELVIN = 1
  CELSIUS = 2
  FAHRENHEIT = 3

  def __init__(self, temperature, unit=KELVIN):
    if unit == Temperature.KELVIN:
      self._temperature = temperature
    elif unit == Temperature.CELSIUS:
      self._temperature = temperature + 273.15
    elif unit == Temperature.FAHRENHEIT:
      self._temperature = (temperature + 459.67) * 5 / 9
    else:
      assert False

  @property
  def k(self):
    return self._temperature

  @property
  def kelvin(self):
    return self._temperature

  @property
  def c(self):
    return self._temperature - 273.15

  @property
  def celsius(self):
    return self.c

  @property
  def f(self):
    return self._temperature * 9 / 5 - 459.67

  @property
  def fahrenheit(self):
    return self.f

  def __cmp__(self, other):
    if isinstance(other, Temperature):
      return cmp(self._temperature, other._temperature)
    else:
      return cmp(self._temperature, other)

  def __str__(self):
    return '{0:.1f}C'.format(self.c)


ZERO_ANGLE = Angle(0, Angle.RADIAN)
ONE_SECOND = Duration(1, Duration.SECOND)
ONE_MINUTE = Duration(1, Duration.MINUTE)
ONE_HOUR = Duration(1, Duration.HOUR)
