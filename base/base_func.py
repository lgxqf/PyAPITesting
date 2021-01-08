# -*- coding: utf-8 -*-
import functools
import inspect
import json
import re
import xmltodict
import traceback
import requests
import time

from .base_request import BaseResponse
from .util import log_config

LOG_LEVEL = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10}

s = requests.Session()
a = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
s.mount('http://', a)


def get_api_prefix(env, host, interface_type):
    if isinstance(host, dict):
        host = host.get('host')
    return '{0}{1}'.format(host, env[host][interface_type])


def flow(func):
    @functools.wraps(func)
    def wrap(config, log):
        __print = globals()['__builtins__']['print']

        def _print(*args):
            log.critical(str(args))

        globals()['__builtins__']['print'] = _print
        if not isinstance(config, dict):
            try:
                config = json.loads(config)
            except:
                config = eval(config)
            log = log_config(filename=log, fix=True)[0]

        s_t = time.time()
        # log.critical('脚本开始时间：%s' % str(round(time.time() - s_t, 2)) + 's')

        BaseService.log = log
        BaseService.log_msg_flag = False
        config['log'] = log

        if 'log_level' in config:
            if config['log_level'].upper() in LOG_LEVEL:
                log.level = LOG_LEVEL[config['log_level'].upper()]
        else:
            log.level = 20

        if 'protocol' in config:
            BaseService.protocol = config['protocol']

        params = {}

        for key in inspect.getfullargspec(func).args:
            if key in config:
                params[key] = config[key]

        result_dict = {"name": func.__name__, "title": func.__doc__, 'result': 'Fail'}

        try:
            result = func(**params)

            if isinstance(result, list):
                response = []

                for elem in result:

                    if elem[1]:
                        response.append({"title": func.__doc__ + elem[0],
                                         "result": "Pass",
                                         "detail": '\n'.join(elem[2:]),
                                         "exec_time": str(round(time.time() - s_t, 2)) + 's'})
                    else:
                        response.append({"title": func.__doc__ + elem[0],
                                         "result": "Fail",
                                         "detail": '\n'.join(elem[2:]),
                                         "exec_time": str(round(time.time() - s_t, 2)) + 's'})
                return response

            else:
                result_dict['exec_time'] = str(round(time.time() - s_t, 2)) + 's'
                ret = result

                if isinstance(result, tuple):
                    result_dict["response"] = result[1]
                    ret = result[0]

                if ret is True:
                    result_dict["result"] = "Pass"

                return [result_dict]
        except Exception as e:
            e = str(traceback.format_exc())
            log.error(e)
            result_dict["reason"] = e

            return [result_dict]

        finally:
            exec_time = str(round(time.time() - s_t, 2))
            result_dict["exec_time"] = exec_time

            log.critical('脚本耗时：%s' % exec_time + 's')
            msg = "Complete running test case : " + func.__name__ + " , result : " + result_dict['result']

            if 'response' in result_dict.keys():
                msg += " , response : " + str(result_dict['response'])

            log.critical(msg="\n\n")
            globals()['__builtins__']['print'] = __print

    return wrap


class BaseService(object):
    api_count = 0
    status_code = 404
    token = None
    log = None
    host = None
    log_msg_flag = False
    protocol = 'http'

    @classmethod
    def api(cls, *args, **kwargs):
        protocol = cls.protocol
        if kwargs.get('protocol'):
            protocol = kwargs.get('protocol')
            del kwargs['protocol']
        _api = WrapperApi(*args, log=cls.log, log_msg_flag=cls.log_msg_flag, protocol=protocol, **kwargs)
        return _api

    @classmethod
    def call_api(cls, req_class, res_class,api_config_class, api_name, env,request_body=None, status_success=200):
        if request_body is None:
            request_body = {}

        inter_config = getattr(api_config_class(), api_name, None)
        # req_class = globals()[api_name + 'Request']
        # res_class = globals()[api_name + 'Response']
        request_body = request_body or req_class.get_default_body()

        res, cls.status_code = cls.api_request(host=cls.host, body=request_body, token=cls.token,
                                               interface_config=inter_config,env=env)

        if cls.status_code == status_success and BaseResponse.check_schema(res, res_class):
            return True, res

        return False, res

    @classmethod
    def api_request(cls, host, body, token, interface_config, env):
        cls.api_count += 1
        url = get_api_prefix(env, host, interface_config.interface_type)

        if body and isinstance(body, dict):
            for key, value in list(body.items()):

                if value and str(value) == "DEL_KEY":
                    cls.__del_key(body, key)

        headers = {"Authorization": token} if token else None

        api = cls.api(url, body=body, headers=headers, protocol=interface_config.protocol, verify=False,
                      **interface_config.interface_const)
        response = api.get_response()
        return response, api.status_code

    @staticmethod
    def __del_key(body, key):
        del body[key]

    @staticmethod
    def __set_key_none(body, key):
        body[key] = None

    @classmethod
    def __convert_interface_const(cls, body, url_config):
        uri = url_config.interface_const['uri']
        uri_keys = re.findall(r'{(.*?)\}', uri)
        for uri_key in uri_keys:
            if uri_key in body.keys():
                uri = uri.replace('{' + uri_key + '}', body[uri_key])
                body.pop(uri_key)
        url_config.interface_const['uri'] = uri
        return body, url_config

    @classmethod
    def check_multiple_api(cls, func, body_list, expect_ret, *args):
        """
        :param func:
        :param body_list:
        :param expect_ret:
        :param args:
        :return:
        """
        ret = True
        fail_list = []
        success_list = []
        count = 0

        for body in body_list:
            count += 1
            actual_ret, res = func(**body)[0:2]
            if expect_ret != actual_ret:
                ret = False
                fail_list.append(f"{getattr(func, '__name__')}, Response: {res}")
            else:
                success_list.append(f"{getattr(func, '__name__')}, Response: {res}")

        cls.print_list_result(success_list, fail_list, str(count))

        return ret, {"success_list": success_list, "fail_list": fail_list}

    @classmethod
    def check_response_keys(cls, res, check_keys) -> bool:
        for keys in check_keys.keys():
            value = cls.find_multilevel_response(res, keys)

            if type(value) is not str:
                if value != check_keys.get(keys):
                    return False
            elif not re.match(check_keys.get(keys), value):
                return False

            return True

    @classmethod
    def find_multilevel_response(cls, res, key, multi=None, multi_key=None):
        """
        :param res:
        :param key: eg: 'userinfo.username'
        :param multi:
        :param multi_key:
        :return:
        """
        for k in key.split('.'):
            res = cls.find_key_params(res, k)

            if multi:
                res_list = []
                for r in res:
                    res_list.append(cls.find_key_params(r, multi_key))
                return res_list

        return res

    @classmethod
    def find_key_params(cls, res, key):
        if isinstance(res, list):
            for d in res:
                result = cls.find_key_params(d, key)
                if result:
                    return result
        if isinstance(res, dict):
            for k, v in res.items():
                if k == key:
                    return v
                result = cls.find_key_params(v, key)
                if result:
                    return result

    @classmethod
    def print_list_result(cls, success_list, fail_list, count=''):
        if len(success_list) > 0:
            cls.log.info(f"Success list: {len(success_list)}")
            for value in success_list:
                cls.log.info(value)
        if len(fail_list) > 0:
            cls.log.info(f"Failed list {len(fail_list)}")
            for value in fail_list:
                cls.log.info(value)
        cls.log.info(
            f"RESULT: Total: {count}, Success count is [{len(success_list)}],  Failed count is [{len(fail_list)}]")

    @classmethod
    def print_result(cls, val):
        """
        用于打印测试结果
        :param val:
        :return: 打印测试结果
        """
        test_result = ""
        if val and isinstance(val, list):
            if "result" in val[0].keys():
                test_result = " " + str(val[0]["result"])
            cls.log.info("=======================Test Result" + test_result + " ========================")
            # result = json.dumps(val, encoding="UTF-8", ensure_ascii=False)
            result = json.dumps(val, ensure_ascii=False)
            cls.log.info(result)
            cls.log.info("==========================================================")


class InterfaceConfig(object):
    def __init__(self, interface_info, interface_type=None, token_required=False, protocol='http'):
        self.interface_const = interface_info
        self.interface_type = interface_type
        self.token_required = token_required
        self.protocol = protocol


class WrapperApi:
    def __init__(self, host, uri, method, body=None, log=None, log_msg_flag=False, timeout=120, protocol='http',
                 headers=None, params=None, verify=False, files=None, data=None):
        self.host = host
        self.uri = uri
        self.method = method
        self.body = {} if body is None else body
        self.data = {} if data is None else data
        self.params = {} if params is None else params
        self.timeout = timeout
        self.protocol = protocol
        if host.split(':')[-1] == '30443':
            self.protocol = 'https'
        self.headers = {} if headers is None else headers
        s.verify = verify
        self.files = files
        self.url = None
        self.response = None
        self.response_time = None
        self.log = log
        self.status_code = None
        if self.log is None:
            self.log_flag = False
        else:
            self.log_flag = True
        self.log_msg_flag = log_msg_flag
        self.log_msg = []

    def request(self):
        t_start = time.time()
        try:
            if not isinstance(self.body, dict):
                self.url = self.protocol + '://' + self.host + self.uri.replace('{}', str(self.body))
            elif self.body == {}:
                self.url = self.protocol + '://' + self.host + self.uri
            else:
                uri_keys = re.findall(r'{(.*?)\}', self.uri)
                for key in uri_keys:
                    if key not in self.body and '[' not in key and '.' not in key:
                        self.uri = self.uri.replace('{' + key + '}', '')
                self.url = self.protocol + '://' + self.host + self.uri.format(**self.body)
            if self.method == 'GET' or self.method == 'DELETE':

                self.response = s.request(self.method, self.url, params=self.body, timeout=self.timeout,
                                          headers=self.headers, data=self.data)
            else:
                self.response = s.request(self.method, self.url, params=self.params, json=self.body, files=self.files,
                                          timeout=self.timeout, headers=self.headers, data=self.data)
        except:
            self.log_msg.append('-' * 120 + '\n' + time.ctime() + '\n' + str(traceback.format_exc()) + '\n')
            if self.log_flag:
                self.log.error('\n' + str(self.method) + ' ' + str(self.url) + '\n' + str(self.body) + '\n' +
                               str(traceback.format_exc()) + '\n' + '-' * 120)
        finally:
            try:
                self.status_code = self.response.status_code
            except:
                pass
            self.response_time = time.time() - t_start
            line_break = '\n{}\n'.format('*' * 90)
            line_break_underline = '\n\n'

            base_info = '{}Request: {}, {}{}'.format(line_break, str(self.method), str(self.url), line_break_underline)
            request_info = '{}Body: {}{}'.format(base_info, json.dumps(self.body), line_break_underline)

            if self.data != '{}':
                request_info = '{}Data: {}{}'.format(request_info, self.data, line_break_underline)

            if {} != self.headers:
                request_info = '{}Headers: {}{}'.format(request_info, json.dumps(self.headers), line_break_underline)

            self.log_msg.insert(0, '-' * 120 + '\n' + time.ctime() + request_info)
            if self.response is not None:
                try:
                    response_info = json.dumps(self.response.json())
                except:
                    response_info = str(self.response.content)
                response_info = 'Response: ' + str(self.response.status_code) + '  ' + \
                                str(int(self.response_time * 1000)) + \
                                'ms  \n' + response_info + '\n' + '-' * 90
                self.log_msg.append(response_info)
                if self.log_flag:
                    self.log.info(request_info + response_info)

    def get_response(self, is_soap=False):
        self.request()
        try:
            if self.log_msg_flag:
                m = self.response.json()
                m['log_msg'] = ''.join(self.log_msg)
                return m
            else:
                if self.response.headers.get('Content-Type').__contains__('text/plain'):
                    if is_soap:
                        return json.loads(json.dumps(xmltodict.parse(self.response.text)))
                    else:
                        return self.response.text
                else:
                    return self.response.json()
        except:
            if self.log_msg_flag:
                return {'log_msg': ''.join(self.log_msg), 'error': 'not_json'}
            else:
                return None
