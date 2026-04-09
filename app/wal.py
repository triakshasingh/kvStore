import json
import os
import threading



class WAL:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()

        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, 'w').close()

    def append(self, entry: dict):
        with self._lock:
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
        

    def replay(self):
        with open(self.path, "r") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)