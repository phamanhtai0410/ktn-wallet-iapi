# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from pymongo import ReturnDocument

from lib import dt_utcnow
from lib.logger import debug
from models import PointLogModel, PointModel
from worker import worker


@worker.task(name="worker.task_add_point", rate_limit='500/s')
def task_add_point(address, amount, log, event):
    _log = {
        **log,
        'address': address,
        'amount': amount,
        'created_by': 'task_add_point'
    }
    debug(f"point name: {PointModel.col.full_name}")
    _before_user = PointModel.col.find_one_and_update(filter={
        'address': address,
        'event': event
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
