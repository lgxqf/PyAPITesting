# -*- coding: utf-8 -*-
import logging
from base.base_func import flow, BaseService
from base.util import log_config
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
    account = "adminX"
    password = "admin_pwd"
    ret, res = service.authorization(account, password)

    return ret, res


if __name__ == '__main__':
    log = log_config(c_level=logging.INFO, f_level=logging.INFO, out_path='/', filename=__file__)[0]
    test_auth_success(HOST, log=log)
