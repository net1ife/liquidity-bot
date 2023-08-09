import web3
from web3 import Web3, exceptions
import time
import logging
from logging.handlers import RotatingFileHandler

# Configuration
NODE_URL = "https://base-mainnet.blastapi.io/18899f62-4e25-4260-aec0-d8c8ca09f056"
MINT_EVENT_TOPIC = "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"
LOG_FILE = "liquidity_logs.txt"
MAX_RETRIES = 3
SLEEP_INTERVAL = 5

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)  # 5 MB per file, two backup logs
logger.addHandler(handler)

def initialize_web3(url):
    w3 = Web3(Web3.HTTPProvider(url))
    if not w3.isConnected():
        raise ConnectionError("Failed to connect to Ethereum node.")
    return w3

def log_liquidity_event(tx):
    log_msg = f"Liquidity added in transaction {tx.hash.hex()} by address {tx['from']}"
    print(log_msg)
    logger.info(log_msg)

def main():
    w3 = initialize_web3(NODE_URL)
    latest_block = w3.eth.block_number
    retries = 0

    while retries < MAX_RETRIES:
        try:
            new_block = w3.eth.block_number
            if new_block != latest_block:
                block = w3.eth.get_block(new_block, full_transactions=True)
                print(f"--- Checking Block #{new_block} ---")

                for tx in block.transactions:
                    receipt = w3.eth.get_transaction_receipt(tx.hash)
                    for log in receipt.logs:
                        if MINT_EVENT_TOPIC in log.topics:
                            log_liquidity_event(tx)

                latest_block = new_block
                retries = 0  # Reset retries if block processed successfully

        except exceptions.BlockNotFound:
            print(f"Block {new_block} not found. Skipping...")
        except Exception as e:
            print(f"Error: {e}")
            retries += 1
            time.sleep(SLEEP_INTERVAL)

        time.sleep(1)

    print("Maximum retries reached. Exiting...")

if __name__ == '__main__':
    main()
