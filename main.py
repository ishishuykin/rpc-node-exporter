import os
import signal
import sys
import time
import logging
import requests
from prometheus_client import start_http_server, Gauge, Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("rpc-exporter")

RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", "9101"))
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "3"))

RPC_LATENCY = Gauge("rpc_request_latency_seconds", "Latency of RPC calls in seconds", ["method"])
LATEST_BLOCK = Gauge("rpc_latest_block_number", "Latest block number reported by RPC")
PEER_COUNT = Gauge("rpc_peer_count", "Number of connected peers")
IS_SYNCING = Gauge("rpc_is_syncing", "Sync status: 1 if synchronizing, 0 if fully synced")
GAS_PRICE_GWEI = Gauge("rpc_gas_price_gwei", "Current network gas price in Gwei")
RPC_STATUS = Gauge("rpc_up", "RPC health status: 1 if responsive, 0 if error")
FAILED_REQUESTS = Counter("rpc_failed_requests_total", "Total count of failed RPC calls", ["method"])

def call_rpc(method: str, params: list = None) -> dict | None:
    if params is None:
        params = []
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    start_time = time.time()
    try:
        response = requests.post(RPC_URL, json=payload, timeout=REQUEST_TIMEOUT)
        latency = time.time() - start_time
        RPC_LATENCY.labels(method=method).set(latency)

        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                return data["result"]
        FAILED_REQUESTS.labels(method=method).inc()
    except Exception as exc:
        logger.debug("RPC call %s failed: %s", method, exc)
        FAILED_REQUESTS.labels(method=method).inc()
    return None

def check_rpc():
    block_raw = call_rpc("eth_blockNumber")
    if block_raw is None:
        RPC_STATUS.set(0)
        return

    RPC_STATUS.set(1)
    LATEST_BLOCK.set(int(block_raw, 16))

    peers_raw = call_rpc("net_peerCount")
    if peers_raw is not None:
        PEER_COUNT.set(int(peers_raw, 16))

    sync_result = call_rpc("eth_syncing")
    if sync_result is not None:
        IS_SYNCING.set(1 if sync_result is not False else 0)

    gas_raw = call_rpc("eth_gasPrice")
    if gas_raw is not None:
        gas_gwei = int(gas_raw, 16) / 1e9
        GAS_PRICE_GWEI.set(gas_gwei)

def handle_shutdown(signum, frame):
    logger.info("Received termination signal %s. Shutting down gracefully...", signum)
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    logger.info("Starting RPC Node Exporter on :%d, targeting %s", EXPORTER_PORT, RPC_URL)
    start_http_server(EXPORTER_PORT)
    while True:
        check_rpc()
        time.sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    main()