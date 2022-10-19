# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource
from pydash import get

from connect import security
from helper.exchange import ExchangeHelper
from schemas.exchange import ExchangeSchema


class ExchangePointResource(Resource):

    @security.http(
        form_data=ExchangeSchema()
    )
    def post(self, form_data):
        _log_id = ExchangeHelper.transfer_point(
            address=get(form_data, 'address').lower(),
            amount=get(form_data, 'amount'),
            signature=get(form_data, 'signature')
        )
        return {
            'log_id': _log_id
        }
