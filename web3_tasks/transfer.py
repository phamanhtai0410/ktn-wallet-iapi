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

from blockchain.abi import nft_abi, erc20_abi
from enums.status import Status
from lib import dt_utcnow
from lib.logger import debug
from models import ExchangeLogModel
from tasks import task_get_transaction_receipt_for_exchange
from wallet import worker

_w3 = Web3()


@worker.task(name="worker.task_transfer", rate_limit='500/s')
def task_transfer(address, amount, token, log_id, event, *args, **kwargs):
    debug("on message")
    _task_id = task_transfer.request.id
    _row = {
        'updated_by': f'task_transfer#{_task_id}',
        'updated_time': dt_utcnow(),
        'status': Status.TRANSFERRING,
        'args': {
            'address': address,
            'amount': amount,
            'token': token,
            'log_id': log_id,
            'event': event
        }
    }
    try:

        _account = task_transfer._tasks[_task_id]
        debug(f'Transfer #{log_id} to {_account.account.address}')
        _public_address = _account.web3.toChecksumAddress(address)
        contract = _account.web3.eth.contract(
            _account.web3.toChecksumAddress(token),
            abi=erc20_abi
        )
        _row['dev_account'] = _account.account.address.lower()
        _amount = _account.to_wei(
            amount=amount,
            decimal="USDT"
        )
        tx = contract.functions.transfer(
            _public_address,
            _amount
        ).buildTransaction({
            'gasPrice': _account.web3.eth.gas_price,
            'nonce': _account.web3.eth.getTransactionCount(_account.account.address)
        })
        signed_tx = _account.account.signTransaction(tx)
        _txn = _account.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        _tx_hash = _txn.hex()
        debug(f"Log tx hash: {_tx_hash}")
        _row['tx_hash'] = _tx_hash
    except Exception as e:
        sentry_sdk.capture_exception()
        traceback.print_exc()
        _row['exception'] = str(e)

    ExchangeLogModel.col.find_one_and_update({
        'log_id': log_id
    }, update={
        '$set': _row
    })
    if get(_row, 'tx_hash'):
        task_get_transaction_receipt_for_exchange.delay(
            tx_hash=get(_row, 'tx_hash'),
            log_id=log_id,
            address=address
        )
    return f"Done: task_transfer#{_task_id}"
