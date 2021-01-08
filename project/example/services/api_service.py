# -*- coding: utf-8 -*-
from base.base_func import BaseService
from project.example.services.api_config import APIConfig, APINameList
from settings import test_env
# Keep this, or [api_name + 'Request'] class wil not be found in globals()
from .request_response import *


class APIService(BaseService):

    @classmethod
    def call_api(cls, api_name, request_body=None, status_success=200, api_config_class=APIConfig, env=test_env):
        return super().call_api(req_class=globals()[api_name + 'Request'], res_class=globals()[api_name + 'Response'],
                                api_config_class=api_config_class, api_name=api_name, env=env,
                                request_body=request_body, status_success=status_success)

    @classmethod
    def authorization(cls, account=None, password=None):
        request_body = {"account": account, "password": password}
        return cls.call_api(api_name=APINameList.Authorization, request_body=request_body)
