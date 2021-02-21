from base.api_type import APIType
from base.base_func import InterfaceConfig


class APINameList(object):
    Authorization = 'Authorization'
    Compare = 'Compare'


class APIConfig:
    Authorization = InterfaceConfig({'method': 'POST', 'uri': '/v1/authorization_internal'}, interface_type=APIType.internal, protocol="https")
    Compare = InterfaceConfig({'method': 'POST', 'uri': '/v1/compares/{image_id}'}, interface_type=APIType.internal, protocol="https")
