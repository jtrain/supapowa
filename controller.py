import Queue
import threading
import time
from collections import defaultdict

class Controller(threading.Thread):
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state
        threading.Thread.__init__(self)

        self._reg = Queue.Queue()
        self._registered = defaultdict(set)

        self._send = Queue.Queue()

    def register(self, name, fn):
        """register a fn to be called when event name occurs."""
        self._reg.put((name, fn))

    def send(self, name, event):
        """send the event object to all who have registered for name."""
        self._send.put((name, event))

    def run(self):
        while True:
            while not self._reg.empty():
                name, fn = self._reg.get()
                self._registered[name].update([fn])

            while not self._send.empty():
                name, event = self._send.get()
                listeners = self._registered[name]
                for fn in listeners:
                    t = threading.Thread(target=fn, args=(event,))
                    t.setDaemon(True)
                    t.start()
            time.sleep(0.05)
