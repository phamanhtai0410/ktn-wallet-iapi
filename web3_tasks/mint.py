# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import traceback

import requests
import sentry_sdk
from pydash import get
from web3 import Web3

from blockchain.abi import nft_abi
from lib.logger import debug
from models import LogWalletModel
from tasks import task_get_transaction_receipt_for_order
from wallet import worker

_w3 = Web3()


@worker.task(name="worker.task_mint_nft", rate_limit='500/s')
def task_mint_nft(address, items, order_id, contract_address, *args, **kwargs):
    debug("on message")
    _task_id = task_mint_nft.request.id
    _update = {
        'updated_by': 'miner'
    }
    try:

        _account = task_mint_nft._tasks[_task_id]
        debug(f'Mining order#{order_id} by {_account.account.address}')
        _public_address = _account.web3.toChecksumAddress(address)
        contract = _account.web3.eth.contract(
            _account.web3.toChecksumAddress(contract_address),
            abi=nft_abi
        )
        debug(f'{items}, {_public_address} {order_id}')
        _items = [{
            'rarity': get(item, 'rarity'),
            'cid': _account.web3.toText(text=get(item, 'cid')),
            'nftType': get(item, 'type')
        } for item in items]
        debug(f"_items {_items}, {_public_address} {_account.web3.toBytes(text=order_id)}")
        tx = contract.functions.mintOrderForDev(
            _items,
            _public_address,
            _account.web3.toBytes(text=order_id)
        ).buildTransaction({
            'gasPrice': _account.web3.eth.gas_price,
            'nonce': _account.web3.eth.getTransactionCount(_account.account.address)
        })
        signed_tx = _account.account.signTransaction(tx)
        _txn = _account.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        _tx_hash = _txn.hex()
        debug(f"Log tx hash: {_tx_hash}")
        _update['tx_hash'] = _tx_hash
    except Exception as e:
        sentry_sdk.capture_exception()
        traceback.print_exc()
        _update['exception'] = str(e)

    LogWalletModel.update_one({
        'task_id': _task_id
    }, obj=_update, worker=True)
    debug(f"send worker, {get(_update, 'tx_hash')}")
    if get(_update, 'tx_hash'):
        task_get_transaction_receipt_for_order.delay(
            tx_hash=get(_update, 'tx_hash'),
            order_id=order_id
        )

    return f"Done: task#{_task_id}"
