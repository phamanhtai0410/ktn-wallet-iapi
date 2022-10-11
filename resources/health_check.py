# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource

from connect import security


class HealthCheck(Resource):

    @security.http(
    )
    def get(self, *args, **kwargs):
        return {}
