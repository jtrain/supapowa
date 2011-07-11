from itertools import count

class Unique(object):
    _shared_state = {}
    _count = count()
    def __init__(self):
        self.__dict__ = self._shared_state

    def generate(self, tag='unique'):
        """return a unique string."""
        return '%s%i' % (tag, self._count.next())




