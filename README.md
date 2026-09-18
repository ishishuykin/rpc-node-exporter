# EVM & High-Throughput RPC Node Exporter

A lightweight Prometheus exporter written in Python for benchmarking and monitoring high-throughput EVM-compatible nodes and RPC endpoints.

### Metrics Tracked
- `rpc_request_latency_seconds`: Latency across standard JSON-RPC calls (`eth_blockNumber`, `net_peerCount`, etc.).
- `rpc_latest_block_number`: Real-time block height.
- `rpc_peer_count`: Number of active node peers.
- `rpc_is_syncing`: Sync state (1 = syncing, 0 = synced).
- `rpc_gas_price_gwei`: Network gas price.
- `rpc_up`: Health status flag (1 = operational, 0 = unreachable).

### Architecture
The service periodically queries target RPC endpoints, translates hex payloads into structured float metrics, and exposes them on `:9101/metrics` for Prometheus scraping.

### Quick Start

1. **Clone repository:**
   ```bash
   git clone https://github.com/ishishuykin/rpc-node-exporter.git
   cd rpc-node-exporter