# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource

from connect import security


class MintResource(Resource):

    @security.http()
    def post(self, form_data):

        return
