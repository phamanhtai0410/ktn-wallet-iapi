# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json

from pydash import get
from web3 import Web3
from web3.datastructures import AttributeDict

tx_hash = '0x55f6df4d499054ca16b4a3d1c1a6fb67abcc265f9d73655543b26f9bca41a70b'

nft_abi = None
with open("blockchain/abi/data/NFT.json") as file:
    nft_abi = json.load(file)  # load contract info as JSON
    file.close()

_web3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545/', request_kwargs={'timeout': 60}))
_txn_receipt = _web3.eth.wait_for_transaction_receipt(tx_hash)
print(_txn_receipt)
_contract = _web3.eth.contract(
    _web3.toChecksumAddress(get(_txn_receipt, 'from')),
    abi=nft_abi
)
_tx_info = _contract.events.MintOrder().processReceipt(_txn_receipt)

print(_tx_info[0].args.returnMintingOrder)
