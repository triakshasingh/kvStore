import json
import socketserver

from wal import WAL
from store import Store


class KVHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            line = self.rfile.readline()
            if not line:
                break

            try:
                request = json.loads(line.decode("utf-8"))
                response = self.process_request(request)
            except json.JSONDecodeError:
                response = {
                    "status": "error",
                    "error": "invalid JSON"
                }
            except Exception as e:
                response = {
                    "status": "error",
                    "error": str(e)
                }

            self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))

    def process_request(self, request):
        op = request.get("op")

        if op == "get":
            key = request.get("key")
            if key is None:
                return {"status": "error", "error": "missing key"}

            value = self.server.store.get(key)
            if value is None:
                return {"status": "not_found"}
            return {"status": "ok", "value": value}

        elif op == "set":
            key = request.get("key")
            if key is None:
                return {"status": "error", "error": "missing key"}
            if "value" not in request:
                return {"status": "error", "error": "missing value"}

            value = request["value"]
            self.server.store.set(key, value)
            return {"status": "ok"}

        elif op == "delete":
            key = request.get("key")
            if key is None:
                return {"status": "error", "error": "missing key"}

            self.server.store.delete(key)
            return {"status": "ok"}

        else:
            return {"status": "error", "error": "unknown op"}


class KVServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, handler_class, store):
        super().__init__(server_address, handler_class)
        self.store = store


def main():
    wal = WAL("kvstore.wal")
    store = Store(wal, capacity=1000)

    host = "127.0.0.1"
    port = 5000

    server = KVServer((host, port), KVHandler, store)
    print(f"Server running on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()