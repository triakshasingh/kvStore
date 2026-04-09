from collections import OrderedDict
from threading import Lock


class Store:
    def __init__(self, wal, capacity=1000):
        self.wal = wal
        self.capacity = capacity
        self.data = {}
        self.lru = OrderedDict()
        self._lock = Lock()

        self._replay_wal()

    def _touch(self, key):
        if key in self.lru:
            self.lru.move_to_end(key)
        else:
            self.lru[key] = None

    def _evict_if_needed(self):
        while len(self.data) > self.capacity:
            oldest_key, _ = self.lru.popitem(last=False)
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

    def get(self, key):
        with self._lock:
            if key not in self.data:
                return None

            self._touch(key)
            return self.data[key]

    def set(self, key, value):
        with self._lock:
            self.wal.append({
                "op": "set",
                "key": key,
                "value": value
            })

            self.data[key] = value
            self._touch(key)
            self._evict_if_needed()

    def delete(self, key):
        with self._lock:
            self.wal.append({
                "op": "delete",
                "key": key
            })

            if key in self.data:
                del self.data[key]
            if key in self.lru:
                del self.lru[key]