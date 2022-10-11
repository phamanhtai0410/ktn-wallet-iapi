# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from eth_account import Account
from web3 import HTTPProvider, Web3
from web3.middleware import construct_sign_and_send_raw_middleware


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

    def change_provider(self, provider):
        self.provider = provider
        self.run_provider()
