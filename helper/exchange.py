# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import uuid

from tasks.exchange import task_record_exchange


class ExchangeHelper:

    @staticmethod
    def transfer_point(address, amount, signature, event):
        _log_id = str(uuid.uuid4())
        task_record_exchange.delay(
            address=address, amount=amount, log_id=_log_id, signature=signature, event=event
        )
        return _log_id
