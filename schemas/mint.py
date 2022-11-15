# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from marshmallow import Schema, EXCLUDE, fields


class ItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    rarity = fields.Int(required=True)
    # cid = fields.Str(required=True)
    # type = fields.Int(required=True)


class MintSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    address = fields.Str(required=True)
    items = fields.List(fields.Nested(ItemSchema), required=True)
    order_id = fields.Str(required=True)
    contract_address = fields.Str(required=True)
    nft_type = fields.Str(default='raw_nft')
