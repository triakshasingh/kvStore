import json
import socket
import time


HOST = "127.0.0.1"
PORT = 5000
NUM_OPS = 100_000
TIMEOUT = 5


def percentile(sorted_values, p):
    if not sorted_values:
        return 0.0
    index = int(p * len(sorted_values))
    if index >= len(sorted_values):
        index = len(sorted_values) - 1
    return sorted_values[index]


def send_request(sock, request):
    message = json.dumps(request) + "\n"
    sock.sendall(message.encode("utf-8"))

    response = sock.recv(4096).decode("utf-8").strip()
    return json.loads(response)


def main():
    latencies_ms = []

    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock:
        start_total = time.perf_counter()

        for i in range(NUM_OPS):
            request = {
                "op": "set",
                "key": f"key{i}",
                "value": i
            }

            start = time.perf_counter()
            response = send_request(sock, request)
            end = time.perf_counter()

            if response.get("status") != "ok":
                print("Error response:", response)
                return

            latency_ms = (end - start) * 1000
            latencies_ms.append(latency_ms)

        end_total = time.perf_counter()

    total_time = end_total - start_total
    throughput = NUM_OPS / total_time

    latencies_ms.sort()
    p50 = percentile(latencies_ms, 0.50)
    p95 = percentile(latencies_ms, 0.95)
    p99 = percentile(latencies_ms, 0.99)

    print(f"Completed {NUM_OPS} operations")
    print(f"Total time: {total_time:.4f} seconds")
    print(f"Throughput: {throughput:.2f} requests/sec")
    print(f"p50 latency: {p50:.4f} ms")
    print(f"p95 latency: {p95:.4f} ms")
    print(f"p99 latency: {p99:.4f} ms")


if __name__ == "__main__":
    main()