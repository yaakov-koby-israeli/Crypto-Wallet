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
