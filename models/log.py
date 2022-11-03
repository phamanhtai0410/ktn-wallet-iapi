# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from lib import DaoModel


class WalletLogDao(DaoModel):
    def __init__(self, *args, **kwargs):
        super(WalletLogDao, self).__init__(*args, **kwargs)


class PointLogDao(DaoModel):
    def __init__(self, *args, **kwargs):
        super(PointLogDao, self).__init__(*args, **kwargs)
