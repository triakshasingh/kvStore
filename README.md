# kvStore

A lightweight, in-memory key-value store written in Python. It supports persistent storage via a Write-Ahead Log (WAL), LRU eviction, and a TCP server interface for network access.

## Features

- **In-memory store** with configurable LRU eviction
- **Write-Ahead Log (WAL)** for crash recovery and durability
- **TCP server** with a simple JSON protocol (get / set / delete)
- **Thread-safe** — concurrent client connections handled via `ThreadingTCPServer`
- **Benchmarking tools** for both local throughput and network latency

## Project Structure

```
kvStore/
├── app/
│   ├── server.py        # TCP server entry point
│   ├── store.py         # In-memory store with LRU eviction
│   ├── wal.py           # Write-Ahead Log for durability
│   ├── bench.py         # Network benchmark (requires running server)
│   └── bench_local.py   # Local in-process benchmark
├── LICENSE
└── README.md
```

## Getting Started

No dependencies beyond the Python standard library.

**Start the server:**

```bash
python3 app/server.py
```

The server listens on `127.0.0.1:5000` by default.

## Protocol

The server communicates over TCP using newline-delimited JSON.

### Set

```json
{"op": "set", "key": "foo", "value": "bar"}
```
Response: `{"status": "ok"}`

### Get

```json
{"op": "get", "key": "foo"}
```
Response: `{"status": "ok", "value": "bar"}` or `{"status": "not_found"}`

### Delete

```json
{"op": "delete", "key": "foo"}
```
Response: `{"status": "ok"}`

## Benchmarks

**Local (in-process, no network overhead):**

```bash
python3 app/bench_local.py
```

**Network (requires server to be running):**

```bash
python3 app/bench.py
```

Both tools report throughput (ops/sec) and p50 / p95 / p99 latencies.

## Configuration

Key parameters are set in `server.py`:

| Parameter  | Default       | Description                        |
|------------|---------------|------------------------------------|
| `host`     | `127.0.0.1`   | Bind address                       |
| `port`     | `5000`        | Bind port                          |
| `capacity` | `1000`        | Max keys before LRU eviction kicks in |
| WAL path   | `kvstore.wal` | Path to the write-ahead log file   |

## How It Works

1. **WAL** — every `set` and `delete` is appended to a log file before being applied in memory. On startup, the WAL is replayed to reconstruct state.
2. **LRU eviction** — once the store reaches `capacity`, the least-recently-used key is evicted to make room.
3. **Server** — each client connection is handled in its own thread; the shared `Store` instance is protected by a lock.

## License

MIT — see [LICENSE](LICENSE).
