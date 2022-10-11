# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json
import traceback

import sentry_sdk
from pydash import get
from web3 import Web3
from web3.exceptions import TransactionNotFound

from blockchain.abi import erc20_abi
from config import Config


class Blockchain(Web3):
    def __init__(self, at_chain, *args, **kwargs):
        print(*args, **kwargs)
        super(Blockchain, self).__init__(*args, **kwargs)
        self.chain = at_chain

    def get_tx_status(self, tx_hash):
        _tx = self.eth.get_transaction_receipt(tx_hash)
        return get(_tx, 'status')

    def get_transfer_info(self, token, tx_hash):
        try:
            _smc = getattr(self, f'{token.lower()}_smc')
            if not _smc:
                return None, None
            _tx = _smc.eth.wait_for_transaction_receipt(tx_hash)
            # _tx = _smc.eth.get_transaction_receipt(tx_hash)
            _log_smc = _smc.events.Transfer().processReceipt(_tx)
            if _log_smc:
                _tx_info = json.loads(Web3.toJSON(_log_smc))
                if isinstance(_tx_info, list) and _tx_info:
                    return _tx_info[0], _tx
        except TransactionNotFound as e:
            return str(e), None
        except:
            sentry_sdk.capture_message()
            traceback.print_exc()
            return -1, None

    def to_wei(self, amount, decimal):
        decimals = {
            '0': 'wei',
            '3': 'kwei',
            '6': 'mwei',
            '9': 'gwei',
            '12': 'szabo',
            '15': 'finney',
            '18': 'ether'
        }
        return self.toWei(amount, get(decimals, str(decimal), 'ether'))
