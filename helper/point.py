# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from tasks import task_add_point


class PointHelper:

    @staticmethod
    def add_point(address, amount, action, event, ref_id):
        _task_id = task_add_point.delay(
            address=address,
            amount=amount,
            log={
                'action': action,
                'ref_id': ref_id
            },
            event=event
        )
        return str(_task_id)
