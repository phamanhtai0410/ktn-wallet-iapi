# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import traceback

import sentry_sdk
from pydash import get
from pymongo import ReturnDocument

from config import Config
from enums.status import Status
from helper.sign import SignHelper
from helper.socket import SocketEmitter
from lib import dt_utcnow
from lib.logger import debug
from models import UserModel, ExchangeLogModel
from web3_tasks.transfer import task_transfer
from worker import worker


@worker.task(name="worker.task_record_exchange", rate_limit='500/s')
def task_record_exchange(address, amount, log_id, signature):
    _change_log = {
        'log_id': log_id,
        'amount': amount,
        'address': address.lower(),
        'signature': signature,
        'created_by': 'task_record_exchange'
    }

    try:

        _user = UserModel.find_one({
            'address': address.lower()
        })
        _change_log['before'] = _user

        if get(_user, 'total_points') < amount:
            _result = {
                'status': Status.FAIL,
                'msg': "Account not enough point."
            }
        else:
            _after_user = UserModel.col.find_one_and_update({
                'address': address.lower()
            }, update={
                '$set': {
                    'updated_by': 'task_record_exchange',
                    'updated_time': dt_utcnow()
                },
                '$inc': {
                    'total_points': - amount,
                    'total_withdraw': amount
                }
            }, return_document=ReturnDocument.AFTER)
            _change_log['after'] = _after_user

            if get(_after_user, 'total_points') < 0:
                # return points to the user from the above query
                UserModel.col.find_one_and_update({
                    'address': address.lower()
                }, update={
                    '$set': {
                        'updated_by': 'task_record_exchange',
                        'updated_time': dt_utcnow()
                    },
                    '$inc': {
                        'total_points': amount,
                        'total_withdraw': - amount
                    }
                })
                _change_log['return_point'] = amount

                _result = {
                    'status': Status.FAIL,
                    'msg': "Account not enough point."
                }
            else:
                debug("Run task task_transfer")
                task_transfer.delay(
                    address=address,
                    amount=amount,
                    token=Config.USDT_ADDRESS,
                    log_id=log_id
                )
                _result = {
                    'status': Status.TRANSFERRING
                }
    except Exception as e:
        sentry_sdk.capture_exception()
        traceback.print_exc()

        _result = {
            'status': Status.ERROR,
            'msg': str(e)
        }

    _change_log['result'] = _result
    SocketEmitter.emit(
        room_id=address,
        event='EXCHANGE',
        value=_result
    )
    ExchangeLogModel.insert_one(_change_log)
    return f"Done record exchange log: {get(_result, 'status')}"
