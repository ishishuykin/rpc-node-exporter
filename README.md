# RPC Node Exporter & Benchmarking Tool

A lightweight Prometheus exporter designed to track latency, block height progression, and availability of high-throughput EVM RPC endpoints.

### Key Features
- Sub-second block time & call latency measurements (`eth_blockNumber`).
- Health and uptime tracking for validator/RPC instances.
- Pre-configured Prometheus metrics endpoint (`:9101/metrics`).
- Ready for Docker Compose deployment.

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/ishishuykin/rpc-node-exporter.git
   cd rpc-node-exporter
