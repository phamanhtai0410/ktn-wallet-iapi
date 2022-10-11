# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
__models__ = ['LogWalletModel']

from config import Config
from connect import connect_db, redis_cluster
from lib import DaoModel
from models.log import WalletLogDao

LogWalletModel = WalletLogDao(col=connect_db.db.wallet_logs, redis=redis_cluster, project=Config.PROJECT, )



