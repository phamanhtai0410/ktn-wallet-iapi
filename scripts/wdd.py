# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json
import os
import traceback
from random import choice
from time import sleep

import sentry_sdk
from redlock import Redlock

from lib.logger import debug
from config import WalletConfig
from scripts.account import AccountWorker


class StoreWallet:

    def __init__(self, providers, chain=None):
        self.chain = chain
        self.accounts = {}
        self.redl = Redlock(WalletConfig.REDLOCK_REDIS, retry_count=2)
        self.tasks = {}
        if providers:
            self.providers = providers
            self.provider = self.providers.pop()
        self._load()

    def _load(self):
        _privates = json.loads(os.getenv(f'PRIVATE_KEYS', '[]'))

        self.accounts = {}
        for _private in _privates:
            _worker = AccountWorker(
                provider=self.provider,
                private_key=_private
            )
            self.accounts[_worker.account.address.lower()] = _worker

    def get_account(self, address):
        if address in self.accounts:
            return self.accounts[address]
        return None

    def get_random(self, task_id):
        _random = None
        max_retry = 4
        while not _random and max_retry > 0:
            debug(f'self.accounts.keys() {self.accounts.keys()}')
            _ac = choice(list(self.accounts.keys()))
            if self.lock(_ac, task_id):
                _random = self.accounts[_ac]
            if not _random:
                max_retry -= 1
                sleep(3)

        return _random

    def get_account_with_lock(self, address, task_id):
        if address in self.accounts:
            if self.lock(address, task_id):
                return self.accounts[address]
        return False

    def key(self, address):
        return f'ktn:pr:red_locked:{self.chain}:{address.lower()}'

    def lock(self, address, task_id):
        _lock = self.redl.lock(self.key(address), WalletConfig.LOCK_TIME)
        if _lock:
            # Remove after task done
            self.tasks[task_id] = _lock
            return True
        return False

    def unlock(self, task_id):
        if task_id in self.tasks:
            try:

                self.redl.unlock(self.tasks[task_id])
                del self.tasks[task_id]

            except:
                traceback.print_exc()
                sentry_sdk.capture_exception()
