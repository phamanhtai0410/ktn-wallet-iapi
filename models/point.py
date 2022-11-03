# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import traceback

import sentry_sdk

from lib import DaoModel


class PointDao(DaoModel):
    def __init__(self, *args, **kwargs):
        super(PointDao, self).__init__(*args, **kwargs)

    def key_of_event(self, event):
        return f'ktn:points:events:{event}'

    def get_rank(self, event, page, page_size):
        if page <= 0:
            page = 1
        _start = (page - 1) * page_size
        _end = page * page_size
        _event_key = self.key_of_event(event)
        _rank = self.redis.zrevrange(_event_key, _start, _end - 1, withscores=True) or []
        _total = self.redis.zcard(_event_key) or 0

        return [{
            'rank': _start + _ind + 1,
            'point': val[1],
            'address': val[0]
        } for _ind, val in enumerate(_rank)],

    def set_rank(self, event, address, point):
        try:
            self.redis.zadd(self.key_of_event(event), {address: point})
        except:
            sentry_sdk.capture_exception()
            traceback.print_exc()

    def get_rank_of(self, event, address):
        return self.redis.zrevrank(self.key_of_event(event), address) + 1
