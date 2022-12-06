# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json

erc20_abi = None
with open("blockchain/abi/data/IERC20.json") as file:
    erc20_abi = json.load(file)  # load contract info as JSON
    file.close()

nft_abi = None
with open("blockchain/abi/data/NFT.json") as file:
    nft_abi = json.load(file)  # load contract info as JSON
    file.close()

nft_box_abi = None
with open("blockchain/abi/data/BOX_NFT.json") as file:
    nft_box_abi = json.load(file)  # load contract info as JSON
    file.close()
