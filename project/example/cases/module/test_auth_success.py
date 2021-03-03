# -*- coding: utf-8 -*-
import logging
import os

from base.base_func import flow, BaseService
from base.util import log_config, Util
from project.example.services.api_service import APIService
from settings import HOST


@flow
def test_auth_success(host, log=None):
    """
    通过用户account 获取token
    :param host: 测试服务器 ip
    :param log: 日志句柄
    :return:
    """
    BaseService.log = log
    BaseService.host = host
    service = APIService()
    account = "admin"
    password = "admin123"
    request_body = {
        "account": account,
        "password": password
    }
    ret, res = service.authorization(request_body)

    return ret, res


if __name__ == '__main__':
    log = log_config(c_level=logging.INFO, f_level=logging.INFO, out_path=Util.get_log_path(),
                     filename=os.path.basename(__file__))[0]
    test_auth_success(HOST, log=log)
