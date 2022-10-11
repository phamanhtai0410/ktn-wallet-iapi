# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from pydash import get

from enums.chain import ChainCodes
from models import LogWalletModel
from web3_tasks import task_mint_nft


class MintHelper:

    @staticmethod
    def mint_nft(form_data):
        _task_id = task_mint_nft.delay(
            chain=ChainCodes.BSC_CHAIN,
            order_id=get(form_data, 'order_id'),
            items=get(form_data, 'items'),
            contract_address=get(form_data, 'contract_address'),
            address=get(form_data, 'address')
        )
        LogWalletModel.insert_one({
            'task_id': _task_id,
            'form_data': form_data
        }, worker=True)
        return _task_id
