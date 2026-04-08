import json
import os
import threading



class WriteAheadLog:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()

        os.makedirs(os.path.dirname(path), exist_ok = True)
        if not os.path.exists(self.path):
            open(self.path, 'w').close()

    def append(self, entry: dict):
        with self._lock:
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
        

    def read(self):
        return self.entries