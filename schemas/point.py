# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from marshmallow import Schema, EXCLUDE, fields, validate

from lib import NotBlank


class PointSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    address = fields.Str(required=True)
    amount = fields.Number(required=True, validate=validate.Range(min=0))
    ref_id = fields.Str(required=True)
    action = fields.Str(required=True, validate=NotBlank())
    event = fields.Str(required=True)
