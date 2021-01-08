from base.api_type import APIType
from base.base_func import InterfaceConfig


class APINameList(object):
    Authorization = 'Authorization'


class APIConfig:
    Authorization = InterfaceConfig(
        {'method': 'POST', 'uri': '/v1/auth'}, interface_type=APIType.public, token_required=False)