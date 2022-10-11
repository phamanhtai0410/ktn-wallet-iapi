# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import traceback

import sentry_sdk
from pydash import get
from web3 import Web3

from blockchain.abi import nft_abi
from lib.logger import debug
from models import LogWalletModel
from wallet import worker

_w3 = Web3()


@worker.task(name="worker.task_mint_nft", rate_limit='500/s')
def task_mint_nft(address, items, order_id, contract_address, *args, **kwargs):
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
        tx = contract.functions.mint(
            [{
                'rarity': get(item, 'rarity'),
                'cid': get(item, 'cid')
            } for item in items],
            _public_address,
            _account.web3.toText(text=order_id)
        ).buildTransaction({
            'gasPrice': _account.web3.eth.gas_price,
            'nonce': _account.web3.eth.getTransactionCount(_account.account.address)
        })
        signed_tx = _account.signTransaction(tx)

        _txn = _account.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        _tx_hash = _txn.hex()
        try:
            _txn_receipt = _account.web3.eth.wait_for_transaction_receipt(_txn)
            _update['status'] = get(_txn_receipt, 'status')
            if get(_txn_receipt, 'status') != 1:
                sentry_sdk.capture_message(
                    f"Failed: Mint nft for order#{order_id} with tx#{_tx_hash}. Please re-check.")
        except:
            sentry_sdk.capture_message(
                f"Warning: Worker can not check status of tx#{_tx_hash} for order#{order_id}. Please re-check.")
            sentry_sdk.capture_exception()
        _update['tx_hash'] = _tx_hash

    except Exception as e:
        sentry_sdk.capture_exception()
        traceback.print_exc()
        _update['exception'] = str(e)

    LogWalletModel.update_one({
        'task_id': _task_id
    }, obj=_update, worker=True)

    return f"Done: task#{_task_id}"
