from base.base_func import BaseService
from .api_config import APINameList, APIConfig
from settings import TEST_ENV
from .request_response import *   # Keep this, or [api_name + 'Request'] class wil not be found in globals()


class APIService(BaseService):

    @classmethod
    def call_api(cls, api_name=None, request_body=None, status_success=200, api_config_class=APIConfig, req_class=None, res_class=None):
        return super().call_api(req_class=globals()[api_name + 'Request'], res_class=globals()[api_name + 'Response'], api_config_class=api_config_class, env=TEST_ENV, api_name=api_name, request_body=request_body, status_success=status_success)

    @classmethod
    def authorization(cls, request_body=None):
        request_body = AuthorizationRequest.get_default_body() if request_body is None else request_body
        api_name = APINameList.Authorization
        ret, res = cls.call_api(api_name=api_name, request_body=request_body)
        return ret, res

    @classmethod
    def compare(cls, request_body=None):
        request_body = CompareRequest.get_default_body() if request_body is None else request_body
        api_name = APINameList.Compare
        ret, res = cls.call_api(api_name=api_name, request_body=request_body)
        return ret, res

