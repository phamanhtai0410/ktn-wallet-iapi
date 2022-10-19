# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from resources.exhange import ExchangePointResource
from resources.health_check import HealthCheck
from resources.iapi import iapi_resources
from resources.mint import MintResource

api_resources = {
    '/common/health_check': HealthCheck,
    **{f'/iapi{k}': val for k, val in iapi_resources.items()},
    '/mint': MintResource,
    '/exchange': ExchangePointResource
}
