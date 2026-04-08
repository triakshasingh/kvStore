from collections import orderedDict
from threading import Lock

class store:
    def __init__(self, wal, capacity = 1000):
        self.data = {}
        self.wal = wal
        self.capacity = capacity
        self.lru = orderedDict()
        self._lock = Lock()


    def _touch(elf, key):
        if key in self.lru:
            self.lru.move_to_end(key)
        else:
            self.lru[key] = None

    def _evict_if_needed(self):
        while len(self.data) > self.capacity:
            oldest_key, _ = self.lru.popitem(last = False)
            del self.data[oldest_key]

    def _replay_wal(self):
        for entry in self.wal.replay():
            op = entry["op"]
            key = entry["key"]
            if op == "set":
                value = entry["value"]
                self.data[key] = value
                self._touch(key)
                self._evict_if_needed()

            elif op == "delete":
                if key in self.data:
                    del self.data[key]
                if key in self.lru:
                    del self.lru[key]  
