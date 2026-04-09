import time
from store import Store


class DummyWAL:
    def append(self, entry):
        pass

    def replay(self):
        return []


CAPACITY = 200_000
NUM_OPS = 100_000

store = Store(DummyWAL(), capacity=CAPACITY)

latencies = []

# Writes
for i in range(NUM_OPS):
    start = time.perf_counter()
    store.set(f"key{i}", i)
    latencies.append((time.perf_counter() - start) * 1_000_000)  # µs

# Reads
for i in range(NUM_OPS):
    start = time.perf_counter()
    store.get(f"key{i}")
    latencies.append((time.perf_counter() - start) * 1_000_000)

latencies.sort()
total = len(latencies)

total_time_sec = sum(latencies) / 1_000_000
throughput = total / total_time_sec

print(f"Throughput: {throughput:,.0f} ops/sec")
print(f"p50: {latencies[int(total*0.50)]:.2f} µs")
print(f"p95: {latencies[int(total*0.95)]:.2f} µs")
print(f"p99: {latencies[int(total*0.99)]:.2f} µs")