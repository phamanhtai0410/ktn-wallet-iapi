# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False
    PROJECT = "wallet-iapi"
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    # Setup db
    MONGO_URI = os.getenv('MONGO_URI')
    # Authentication
    AUTH_ADDRESS = os.getenv('AUTH_ADDRESS', '')

    CELERY_IMPORTS = ['tasks']
    ENABLE_UTC = True

    # Config celery worker

    BROKER_URL = os.getenv('BROKER_URL')
    CELERY_QUEUES = os.getenv('CELERY_QUEUES')

    CELERY_ROUTES = {
        'worker.task_mint_nft': {'queue': 'ktn-wallet-tx-queue'},
        'worker.task_get_transaction_receipt_for_order': {'queue': 'wallet-receipt-tx-queue'}
    }
    PUBLIC_PATH = os.getenv('PUBLIC_PATH')
    REDIS_CLUSTER = json.loads(os.getenv('REDIS_CLUSTER'))
    ADDRESS_OF_COUNTER = os.getenv('ADDRESS_OF_COUNTER')
    REDLOCK_REDIS = json.loads(os.getenv('REDLOCK_REDIS', '[]'))
    BSC_RPC_URI = os.getenv('BSC_RPC_URI')
    ETH_RPC_URI = os.getenv('ETH_RPC_URI')
    ASSETS = json.loads(os.getenv('ASSETS', '{}'))
    NFT_IAPI = os.getenv('NFT_IAPI')


class WalletConfig:
    DEBUG = False
    PROJECT = "wallet-iapi"
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    # Setup db
    MONGO_URI = os.getenv('MONGO_URI')
    # Authentication
    AUTH_ADDRESS = os.getenv('AUTH_ADDRESS', '')

    CELERY_IMPORTS = ['web3_tasks']
    ENABLE_UTC = True

    # Config celery worker

    BROKER_URL = os.getenv('BROKER_URL')
    CELERY_QUEUES = os.getenv('CELERY_QUEUES')

    CELERY_ROUTES = {
        'worker.task_get_transaction_receipt_for_order': {'queue': 'wallet-receipt-tx-queue'},
        'worker.task_mint_nft': {'queue': 'ktn-wallet-tx-queue'}
    }

    REDLOCK_REDIS = json.loads(os.getenv('REDLOCK_REDIS', '[]'))
    LOCK_TIME = 60 * 5
    BSC_RPC_URI = os.getenv('BSC_RPC_URI')
    ETH_RPC_URI = os.getenv('ETH_RPC_URI')
