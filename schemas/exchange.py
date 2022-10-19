# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from marshmallow import Schema, EXCLUDE, fields


class ExchangeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    address = fields.Str(required=True)
    amount = fields.Float(required=True)
    signature = fields.Dict(required=True)
