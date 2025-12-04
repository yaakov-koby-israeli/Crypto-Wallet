from web3 import Web3

from app.configuration.config import settings

ganache_url = settings.GANACHE_URL
web3_ganache = Web3(Web3.HTTPProvider(ganache_url))

def ensure_account_exists_on_ganache(public_key: str) -> None:
    """
    Validate that the provided address is a valid Ethereum address
    and is present in the connected Ganache node's accounts list.
    """
    if not web3_ganache.is_address(public_key):
        raise ValueError("Invalid Ethereum address")

    ganache_accounts = [acct.lower() for acct in web3_ganache.eth.accounts]
    if public_key.lower() not in ganache_accounts:
        raise ValueError("Public key not found on Ganache")

# Get the balance of an Ethereum account
def get_account_balance_from_blockchain(user_public_key) -> float:

    balance_wei = web3_ganache.eth.get_balance(user_public_key)
    return web3_ganache.from_wei(balance_wei, 'ether')

def get_transactions_for_address(address: str, start_block: int | None = None, end_block: int | None = None) -> list[dict]:
    """
    Fetch all transactions involving the given address (as sender or recipient)
    between start_block and end_block (inclusive). Defaults to the full chain.
    """
    if not web3_ganache.is_address(address):
        raise ValueError("Invalid Ethereum address")

    latest_block = web3_ganache.eth.block_number
    start = 0 if start_block is None else start_block
    end = latest_block if end_block is None else end_block

    address_lower = address.lower()
    txs: list[dict] = []

    for block_number in range(start, end + 1):
        block = web3_ganache.eth.get_block(block_number, full_transactions=True)
        for tx in block.transactions:
            tx_from = (tx["from"] or "").lower()
            tx_to = (tx["to"] or "").lower() if tx["to"] else ""
            if address_lower in (tx_from, tx_to):
                txs.append({
                    "hash": tx["hash"].hex(),
                    "from": tx["from"],
                    "to": tx["to"],
                    "value_eth": float(web3_ganache.from_wei(tx["value"], "ether")),
                    "block_number": tx["blockNumber"],
                    "nonce": tx["nonce"],
                    "gas": tx["gas"],
                    "gas_price_wei": tx["gasPrice"],
                })

    return txs

# Sends ETH using Ganache and returns the transaction hash as a hex string
def send_eth(from_address: str, to_address: str, amount: float) -> str:
    transaction = {
        "from": from_address,
        "to": to_address,
        "value": web3_ganache.to_wei(amount, "ether"),
        "gas": 21000,
        "gasPrice": web3_ganache.to_wei(1, "gwei"),
        "nonce": web3_ganache.eth.get_transaction_count(from_address),
        "chainId": web3_ganache.eth.chain_id,
    }

    tx_hash = web3_ganache.eth.send_transaction(transaction)

    receipt = web3_ganache.eth.wait_for_transaction_receipt(tx_hash)
    if(receipt.status == 0):
        raise ValueError(f"Transaction failed! Reverted. Hash: {tx_hash.hex()}")

    return tx_hash.hex()
