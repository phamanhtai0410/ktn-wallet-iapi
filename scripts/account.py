# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import traceback

import sentry_sdk
from eth_account import Account
from pydash import get
from web3 import HTTPProvider, Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from blockchain import erc20_abi
from config import Config
from enums.chain import ChainCodes


class AccountWorker:

    def run_provider(self):
        self.web3 = Web3(HTTPProvider(self.provider))

        self.web3.middleware_onion.add(
            construct_sign_and_send_raw_middleware(self.account)
        )

        self.web3.eth.default_account = self.account.address

    def __init__(self, provider: str, private_key: str):
        self.account = Account.from_key(private_key)
        self.provider = provider
        self.web3 = None
        # run provider
        self.run_provider()
        self.decimals = {}

    def change_provider(self, provider):
        self.provider = provider
        self.run_provider()

    @property
    def usdt_smc(self):
        try:
            if not get(Config.ASSETS, f'{ChainCodes.BSC_CHAIN}.USDT'):
                return None
            _smc = self.web3.eth.contract(
                self.web3.toChecksumAddress(get(Config.ASSETS, f'{ChainCodes.BSC_CHAIN}.USDT')),
                abi=erc20_abi
            )
            self.decimals['USDT'] = _smc.functions.decimals().call()
            return _smc
        except:
            sentry_sdk.capture_exception()
        return None

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
        return self.web3.toWei(amount, get(decimals, str(decimal), 'ether'))
