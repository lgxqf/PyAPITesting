# -*- coding: utf-8 -*-
import copy
import inspect
from abc import ABCMeta, abstractmethod
from jsonschema import validate, ValidationError, SchemaError


class Message(object):
    @classmethod
    def obj_key(cls, obj):
        """
        :param obj:
        :return:
        """
        for obj_key in dir(cls):
            obj_value = getattr(cls, obj_key)
            if obj_value == obj:
                return obj_key
        return ""

    @classmethod
    def keys(cls):
        keys = []
        for obj_key in dir(cls):
            if obj_key.startswith('__'):
                continue
            obj_value = getattr(cls, obj_key)
            if isinstance(obj_value, str):
                keys.append(obj_key)
            elif inspect.isclass(obj_value):
                keys.append({obj_key: obj_value.keys()})
        return keys


class BaseRequest(Message):
    __metaclass__ = ABCMeta
    # about __metaclass__ https://www.jianshu.com/p/224ffcb8e73e

    @abstractmethod
    def get_request(self):
        pass

    @classmethod
    def convert_param(cls, key, param):
        result = []
        for param_dict in param:
            invalid_value, error = param_dict[:2]
            temp = {'key': key, 'value': invalid_value, 'error': error}
            if len(param_dict) == 3:
                status_code = param_dict[2]
                temp['status_code'] = status_code
            result.append(temp)
        return result

    @classmethod
    def get_param_value(cls):
        """
        得到默认请求体、无效请求体、边界值请求体，通常用于获得不同的request_body
        :return: 默认请求体、无效请求体、边界值请求体
        """
        request_dict = cls().get_request()
        default_body = {}
        valid_list = []
        invalid_params_list = []

        for key, value in request_dict.items():
            if value.get('invalid'):
                invalid_params_list.extend(cls.convert_param(key, value['invalid']))

            if value.get('boundary'):
                invalid_params_list.extend(cls.convert_param(key, value['boundary']))

            valid_value = value['valid'][0]
            default_body[key] = valid_value

        valid_list.append(default_body)

        return default_body, invalid_params_list, valid_list

    @classmethod
    def get_default_body(cls) -> object:
        """
        得到默认值请求体
        :return:
        """
        return cls.get_param_value()[0]

    @classmethod
    def get_invalid_params(cls):
        """
        得到无效请求体, 通常用于批量参数校验
        :return:
        """
        return cls.get_param_value()[1]

    @classmethod
    def get_boundary_list(cls):
        """
        得到边界值请求体
        :return:
        """
        return cls.get_param_value()[2]


class BaseResponse(Message):
    @classmethod
    def get_expect_keys(cls):
        return copy.deepcopy(cls.keys())

    @classmethod
    def check_schema(cls, res, expect):
        """
        Check the response result type and format
        :param res: api response
        :param expect: api expected results
        :return: bool
        """

        try:
            error_info = validate(res, expect.schema)
            if error_info is not None:
                print(str(error_info))
                return False
        except ValidationError as e:
            print(e)
            return False
        except SchemaError as e:
            print(e)
            return False
        return True

    def check_format(self, res, keys_list=None):
        if isinstance(res, dict):
            for k, v in res.copy().items():
                keys_list.append(k)
                if isinstance(v, dict):
                    self.check_format(v, keys_list)
                else:
                    continue
        return keys_list


# class GetRequestData(Message):
#     @staticmethod
#     def get_param_value(request_body, body_type):
#         """
#         得到默认请求体、无效请求体、边界值请求体，通常用于获得不同的request_body
#         :return: 默认请求体、无效请求体、边界值请求体
#         """
#         request_dict = request_body
#         valid_body = {}
#         body_list = []
#         body_dict = {}
#         body_dict1 = {}
#         for key, value in request_dict.items():
#             if body_type == 'valid':
#                 valid_body[key] = value.get(body_type)
#             elif body_type == 'left_boundary' in value:
#                 body_dict[key] = value.get(body_type)[0]
#                 body_dict1[key] = value.get(body_type)[1]
#             elif body_type == 'right_boundary' in value:
#                 body_dict[key] = value.get(body_type)[0]
#                 body_dict1[key] = value.get(body_type)[1]
#             elif body_type == 'invalid' in value:
#                 body_list.append({'key': key, 'value': value.get(body_type), 'error': ""})
#         body_list.append(body_dict)
#         body_list.append(body_dict1)
#         return valid_body, body_list
