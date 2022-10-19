# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from eth_account.messages import defunct_hash_message

from lib.utils import util_web3


class SignHelper:

    @staticmethod
    def get_address_of_signature(signature, msg):
        _msg_hash = defunct_hash_message(text=msg)

        return util_web3.eth.account.recoverHash(
            _msg_hash,
            signature=signature
        )
