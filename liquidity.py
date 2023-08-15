import web3
from web3 import Web3, exceptions
import time

w3 = Web3(Web3.HTTPProvider("https://base-mainnet.blastapi.io/18899f62-4e25-4260-aec0-d8c8ca09f056"))

# Define the topics for the Mint event
mint_event_topic = "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"

# Get the latest block
latest_block = w3.eth.block_number

# Define the file to store the logs
logfile = "liquidity_logs.txt"

while True:
    new_block = w3.eth.block_number
    if new_block != latest_block:
        try:
            # Fetch the new block and get the transactions
            block = w3.eth.get_block(new_block, full_transactions=True)
            print(f"--- Checking Block #{new_block} ---")

            # Iterate through all transactions in the block
            for tx in block.transactions:
                # Get the receipt to access the logs
                receipt = w3.eth.get_transaction_receipt(tx.hash)
                # Iterate through each log
                for log in receipt.logs:
                    # Check if this log's topics contain the Mint event topic
                    if mint_event_topic in log['topics']:
                        log_msg = f"Liquidity added in transaction {tx.hash.hex()} by address {tx['from']}"
                        print(log_msg)

                        # Also write it into the log file
                        with open(logfile, "a") as f:
                            f.write(log_msg + "\n")

            latest_block = new_block

        except exceptions.BlockNotFound:
            print(f"Block {new_block} not found. Skipping...")

    time.sleep(1)
