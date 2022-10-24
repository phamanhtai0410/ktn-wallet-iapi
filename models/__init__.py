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
from models.log import WalletLogDao, PointLogDao
from models.nft import NFTDao

LogWalletModel = WalletLogDao(col=connect_db.db.wallet_logs, redis=redis_cluster, broker=Config.BROKER_URL,
                              project=Config.PROJECT)

ExchangeLogModel = DaoModel(col=connect_db.db.exchange_logs, redis=redis_cluster, broker=Config.BROKER_URL,
                            project=Config.PROJECT)

NFTModel = NFTDao(col=connect_db.db.nfts, redis=redis_cluster, broker=Config.BROKER_URL, project=Config.PROJECT)
UserModel = DaoModel(col=connect_db.db.user, redis=redis_cluster, broker=Config.BROKER_URL, project=Config.PROJECT)
PointLogModel = PointLogDao(col=connect_db.db.point_logs, redis=redis_cluster)
PointModel = DaoModel(col=connect_db.db.points, redis=redis_cluster)
