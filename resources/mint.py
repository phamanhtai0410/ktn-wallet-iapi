# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource

from connect import security
from helper.mint import MintHelper
from schemas.mint import MintSchema


class MintResource(Resource):

    @security.http(
        form_data=MintSchema()
    )
    def post(self, form_data):
        _task_id = MintHelper.mint_nft(form_data)
        return {
            'task_id': _task_id
        }
