# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from pymongo import ReturnDocument

from lib import dt_utcnow
from models import UserModel, PointLogModel
from worker import worker


@worker.task(name="worker.task_add_point", rate_limit='500/s')
def task_add_point(address, amount, log):
    _log = {
        **log,
        'address': address,
        'amount': amount,
        'created_by': 'task_add_point'
    }
    _before_user = UserModel.col.find_one_and_update(filter={
        'address': address
    }, update={
        '$set': {
            'updated_time': dt_utcnow(),
            'updated_by': 'task_add_point'
        },
        "$inc": {
            'total_points': amount
        }
    }, return_document=ReturnDocument.BEFORE)

    _log['before'] = _before_user
    PointLogModel.insert_one(_log)
    return f"Done add point for {address}"
