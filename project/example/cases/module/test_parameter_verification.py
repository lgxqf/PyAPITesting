# -*- coding: utf-8 -*-
import logging

from base.base_func import *
from settings import HOST


@flow
def test_parameter_verification(host, log=None):
    """
    测试用例样例
    :param host: 测试服务器
    :param log: 日志句柄，由sep平台传入
    :return:
    """

    BaseService.log = log
    BaseService.host = host

    return True


if __name__ == '__main__':
    log = log_config(c_level=logging.INFO, f_level=logging.INFO, out_path='/', filename=__file__)[0]
    test_parameter_verification(HOST, log=log)
