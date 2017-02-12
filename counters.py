import time

class Counter(object):
    def increase(self):
        self.add(1)

    def add(self, value):
        raise NotImplementedError()

    def count(self):
        raise NotImplementedError()

    def sum(self):
        raise NotImplementedError()

    def average(self):
        total_count = self.count()
        if total_count == 0:
            return 0
        else:
            return float(self.sum()) / total_count


class PerfCounter(Counter):
    def __init__(self, name, time_func=time.time):
        self._name = name
        self._total = SingleCounter()
        self._last_hour = RecentCounter(resolution=60, size=60, time_func=time_func)
        self._last_minute = RecentCounter(resolution=1, size=60, time_func=time_func)

    @property
    def name(self):
        return self._name    

    def add(self, value):
        self._total.add(value)
        self._last_hour.add(value)
        self._last_minute.add(value)

    def count(self):
        return self._total.count()

    def sum(self):
        return self._total.sum()

    @property
    def total(self):
        return self._total

    @property
    def last_hour(self):
        return self._last_hour

    @property
    def last_minute(self):
        return self._last_minute

    def __str__(self):
        return '{0}: {1}, {2}\n\tlast hour: {3}, {4}\n\tlast_minute: {5}, {6}'.format(
            self._name,
            self._total.sum(), self._total.average(),
            self._last_hour.sum(), self._last_hour.average(),
            self._last_minute.sum(), self._last_minute.average())


class SingleCounter(Counter):
    def __init__(self):
        self._sum = 0
        self._count = 0

    def add(self, value):
        self._sum += value
        self._count += 1

    def count(self):
        return self._count

    def sum(self):
        return self._sum


class RecentCounter(Counter):
    def __init__(self, resolution, size, time_func=time.time):
        self._time_func = time_func
        self._resolution = resolution
        self._size = size
        self._values = [0] * size
        self._counters = [0] * size 
        self._last_index = 0
        self._origin = self._now()

    def add(self, value):
        self._refresh()
        self._values[self._last_index % self._size] += value
        self._counters[self._last_index % self._size] += 1

    def count(self):
        self._refresh()
        return sum(self._counters)

    def sum(self):
        self._refresh()
        return sum(self._values)

    def _refresh(self):
        now = self._now()
        new_index = int((now - self._origin) / self._resolution)
        offset = new_index - self._last_index

        for i in range(0, min(offset, self._size)):
            self._last_index = self._last_index + 1
            self._values[self._last_index % self._size] = 0
            self._counters[self._last_index % self._size] = 0

        self._last_index = new_index

    def _now(self):
        return self._time_func()


class Aggregator(object):
    def __init__(self, size):
        self._size = size
        self._data = [0] * size
        self._index = 0
        self._count = 0

    def add(self, value):
        self._data[self._index] = value
        self._index = (self._index + 1) % self._size
        self._count = min(self._count + 1, self._size)

    def average(self):
        if self._count == 0:
            return 0
        else:
            return float(sum(self._data)) / self._count

    def max(self):
        if self._count == self._size:
            return max(self._data)
        elif self._count == 0:
            return 0
        else:
            return max(self._data[0:self._index])

    def max(self):
        if self._count == self._size:
            return min(self._data)
        elif self._count == 0:
            return 0
        else:
            return min(self._data[0:self._index])