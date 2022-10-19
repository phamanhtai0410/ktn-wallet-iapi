# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource
from marshmallow import EXCLUDE
from pydash import get

from connect import security
from helper.point import PointHelper
from schemas.point import PointSchema


class PointResource(Resource):

    @security.http(
        form_data=PointSchema()
    )
    def post(self, form_data):

        task_id = PointHelper.add_point(
            address=get(form_data, 'address').lower(),
            amount=get(form_data, 'amount'),
            action=get(form_data, 'action'),
            ref_id=get(form_data, 'ref_id')
        )

        return {
            'task_id': task_id
        }
