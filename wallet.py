# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""

import sentry_sdk
from celery import Task, Celery
from flask import Flask
from pydash import find, get
from sentry_sdk import capture_message
from sentry_sdk.integrations.flask import FlaskIntegration

from connect import connect_db
from enums.chain import ChainCodes
from config import WalletConfig, Config
from lib.logger import debug
from scripts.wdd import StoreWallet


class Wallet(Task):
    _chain = {}
    _tasks = {}

    def __init__(self):

        _eth_providers = [WalletConfig.ETH_RPC_URI]
        _bsc_providers = [WalletConfig.BSC_RPC_URI]
        debug("_bsc_providers", _bsc_providers)
        self._chain = {
            ChainCodes.ETHEREUM_CHAIN: StoreWallet(
                providers=_eth_providers.copy(),
                chain=ChainCodes.ETHEREUM_CHAIN
            ),
            ChainCodes.BSC_CHAIN: StoreWallet(
                providers=_bsc_providers.copy(),
                chain=ChainCodes.BSC_CHAIN
            )
        }

    def before_start(self, task_id, args, kwargs):
        """
            - Get one account

        """
        _chain = get(kwargs, 'chain')
        debug(f'before start {_chain}')
        if not _chain:
            _chain = ChainCodes.BSC_CHAIN
            kwargs['chain'] = _chain

        if not _chain:
            raise Exception("Task - Noy found chain")
        _account = None
        if 'force_account' in kwargs:
            _account = self._chain[_chain].get_account_with_lock(address=kwargs['force_account'], task_id=task_id)
        else:
            _account = self._chain[_chain].get_random(task_id=task_id)

        if not _account:
            self.retry()

        self._tasks[task_id] = _account

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        _account = self._tasks[task_id]
        del self._tasks[task_id]
        _chain = get(kwargs, 'chain')
        self._chain[_chain].unlock(task_id)


def create_app(config):
    print('config', config)
    app = Flask('Wallet', instance_relative_config=True)
    configure_app(app, config)
    configure_extensions(app)

    return app


def configure_app(app, config):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)


def configure_extensions(app):
    # flask-sqlalchemy
    # db.init_app(app)
    # Init database
    connect_db.init_app(app, Config.MONGO_URI)

    # Sentry
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            debug=True,
            server_name="Wallet"
        )

        capture_message('Setup wallet done')


def wallet_worker(config):
    app = create_app(config)
    debug("app.config['BROKER_URL']", app.config['BROKER_URL'])
    celery = Celery("wallet",
                    broker=app.config['BROKER_URL'],
                    task_cls='wallet:Wallet'
                    )
    celery.conf.update(app.config)
    TaskBase = celery.Task
    debug('Init Celery tasks app')

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


worker = wallet_worker(WalletConfig)
