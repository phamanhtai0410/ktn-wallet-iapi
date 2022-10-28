# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json
import traceback

import requests
import sentry_sdk
from pydash import get

from blockchain.abi import nft_abi, erc20_abi
from config import Config
from connect import web3_providers
from enums.order import Chains
from enums.status import Status
from helper.socket import SocketEmitter
from lib.logger import debug
from models import LogWalletModel, ExchangeLogModel
from worker import worker


@worker.task(name="worker.task_get_transaction_receipt_for_order", rate_limit='500/s')
def task_get_transaction_receipt_for_order(tx_hash, order_id):
    _update = {
        'updated_by': 'task_get_transaction_receipt_for_order'
    }
    try:
        _web3 = web3_providers[Chains.BSC_CHAIN]
        _txn_receipt = _web3.eth.wait_for_transaction_receipt(tx_hash)

        _update['status'] = get(_txn_receipt, 'status')
        if get(_txn_receipt, 'status') != 1:
            sentry_sdk.capture_message(
                f"Failed: Mint nft for order#{order_id} with tx#{tx_hash}. Please re-check.")
        else:
            debug(f'{_txn_receipt}')
            debug(f'{get(_txn_receipt, "from")}')
            debug(f"{web3_providers[Chains.BSC_CHAIN].toChecksumAddress(get(_txn_receipt, 'from'))}")
            debug(f"{nft_abi}")

            _contract = _web3.eth.contract(
                web3_providers[Chains.BSC_CHAIN].toChecksumAddress(get(_txn_receipt, 'from')),
                abi=nft_abi
            )
            _tx_info = _contract.events.MintOrderForDev().processReceipt(_txn_receipt)

            debug(f'info: {_tx_info}')

            if len(_tx_info) == 0:
                raise Exception("Failed: Cannot get info of order.")

            _tx_info = _tx_info[0]
            _items = _tx_info.args.returnMintingOrder
            _to = _tx_info.args.to

            _token_ids = [{
                'token_id': _token_id,
                'rarity': _rarity,
                'cid': _cid,
                'type': _type
            } for (_token_id, _rarity, _cid, _type) in _items]

            _update['MintOrder'] = _token_ids

            res = requests.put(f'{Config.NFT_IAPI}/iapi/order', json={
                'order_id': order_id,
                'tx_hash': tx_hash,
                'token_ids': _token_ids,
                'address': _to.lower()
            }, timeout=10)
            debug(res.text)
            if res.status_code != 200:
                sentry_sdk.capture_message(f"Failed: Send completed order#{order_id}. Error: {res.text}")

    except Exception as e:
        sentry_sdk.capture_message(
            f"Warning: Worker can not check status of tx#{tx_hash} for order#{order_id}. Please re-check.")
        sentry_sdk.capture_exception()
        _update['exception'] = str(e)
        traceback.print_exc()
    LogWalletModel.update_one({
        'tx_hash': tx_hash
    }, obj=_update)

    return f"Done: get log for order#{order_id}"


@worker.task(name="worker.task_get_transaction_receipt_for_exchange", rate_limit='500/s')
def task_get_transaction_receipt_for_exchange(tx_hash, log_id, address):
    _update = {
        'updated_by': 'task_get_transaction_receipt_for_exchange'
    }

    try:
        _web3 = web3_providers[Chains.BSC_CHAIN]
        _txn_receipt = _web3.eth.wait_for_transaction_receipt(tx_hash)

        _update['status'] = Status.OKE if get(_txn_receipt, 'status') else Status.ERROR

        if get(_txn_receipt, 'status') != 1:
            _update['msg'] = 'Pending check tx hash.'
            sentry_sdk.capture_message(
                f"Failed: transfer log#{log_id} with tx#{tx_hash}. Please re-check.")

    except Exception as e:
        sentry_sdk.capture_message(
            f"Warning: Worker can not check status of tx#{tx_hash} for order#{log_id}. Please re-check.")
        sentry_sdk.capture_exception()
        _update['exception'] = str(e)

        traceback.print_exc()
    ExchangeLogModel.update_one({
        'log_id': log_id
    }, obj=_update)
    result = {
        'status': get(_update, 'status'),
        'tx_hash': get(_update, 'tx_hash') or tx_hash,
        'msg': get(_update, 'msg') or "Successfully"
    }
    SocketEmitter.emit(
        room_id=address,
        event='EXCHANGE',
        value=result
    )
    return f"Done: get log for tx#{tx_hash}"
