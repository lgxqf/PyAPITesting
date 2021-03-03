import logging
import os
import string
import time

from random import sample
from base.api_type import APIType
from settings import project_root
from logging.handlers import RotatingFileHandler


def log_config(f_level=logging.INFO, c_level=logging.CRITICAL, out_path='', filename='info', fix=False):
    logfile = os.path.join(out_path, filename) + '-' + time.strftime('%Y_%m%d_%H%M%S', time.localtime()) + '.log' \
        if not fix else os.path.join(out_path, filename) + '.log'
    logger = logging.getLogger(logfile)

    if f_level is None:
        if c_level is None:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(c_level)
    else:
        logger.setLevel(f_level)

    formatter = logging.Formatter(
        '[%(levelname)s][%(process)d][%(thread)d]--%(asctime)s--[%(filename)s %(funcName)s %(lineno)d]: %(message)s')

    if c_level is not None:
        ch = logging.StreamHandler()
        ch.setLevel(c_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if f_level is not None:
        fh = RotatingFileHandler(logfile, maxBytes=1000 * 1024 * 1024, backupCount=100)
        fh.setLevel(f_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger, logfile


class Util:
    """
        Add ID and Project field for test case file
        project_name: project name
        path_list: case directory list
    """

    @classmethod
    def create_dir(cls, path):
        if not os.path.exists(path):
            os.makedirs(path)

    @classmethod
    def get_log_path(cls, dir_name='log',project_name="PyAPITesting"):
        cwd = os.path.dirname(os.path.realpath(__file__))
        dir_index = cwd.rindex(project_name)
        log_path = cwd[: dir_index + len(project_name)] + os.sep + 'test_results' + os.sep + dir_name
        return log_path

    # @classmethod
    # def get_project_path(cls, dir_name=None):
    #     cwd = os.path.dirname(os.path.realpath(__file__))
    #
    #     root_name = project_root
    #     dir_index = cwd.rindex(root_name)
    #     return cwd[: dir_index + len(root_name)] + os.sep + dir_name

    @classmethod
    def get_project_home(cls):
        cwd = os.path.dirname(os.path.realpath(__file__))
        dir_index = cwd.rindex(project_root)
        return cwd[: dir_index + len(project_root)]

    @classmethod
    def get_random_len(cls, data_len=128, data_type=int, r_float=1):
        data_list = sample('1234567890' * (data_len // 10 + 1), data_len)
        result = ''.join(str(i) for i in data_list)

        if data_type == int:
            return int(result)

        elif data_type == str:
            result = ''
            while data_len > 0:
                result += result.join(sample(string.digits, 1))
                data_len -= 1
            return result

        elif data_type == float:
            if data_len == 1:
                return result + '.000000'

            return result[:data_len - r_float] + '.' + result[-r_float:]

    @classmethod
    def add_test_id(cls, project_name, path_list=None):
        if path_list is None:
            path_list = []
        case_write_list = []

        for case_path in path_list:
            case_file = []

            for r, d, f in os.walk(case_path):
                for item in f:
                    if item.endswith('.py') and '__init__' not in item:
                        case_file.append(os.path.join(r, item))

            for test_case in case_file:
                case_title = str(test_case.split(os.path.sep)[-1]).replace(".py", "")

                with open(test_case, 'r', errors='ignore') as f:
                    file_content = ""
                    content = f.readlines()
                    has_id_field = False

                    for line in content:
                        if "[Project]" in line:
                            file_content = None
                            break

                        if "[ID]" in line:
                            line = "     [Project] " + project_name + "\n" + line
                            has_id_field = True

                        if "[API]" in line and not has_id_field:
                            line = "     [Project] " + project_name + "\n"
                            line += "     [ID] " + case_title + "\n" + line

                        file_content += line

                if file_content:
                    with open(test_case, 'w', errors='ignore') as f:
                        f.write(file_content)
                        case_write_list.append(test_case)

        for test_case in case_write_list:
            print(test_case)

        print(str(len(case_write_list)) + " cases add ID field")

    @classmethod
    def get_api_name(cls, api_name):
        new_name = [api_name[0]]

        # AlertNewDBAddME->alert_new_db_add_me
        continuous_upper_letter_count = 0

        api_name_len = len(api_name)

        for index in range(1, len(api_name)):
            letter = api_name[index]

            if letter.islower():
                continuous_upper_letter_count = 0
                new_name.append(letter)
            else:
                continuous_upper_letter_count += 1
                if continuous_upper_letter_count == 1:
                    new_name.append("_" + letter)

                elif continuous_upper_letter_count > 1 and index + 1 < api_name_len and api_name[index + 1].islower():
                    new_name.append("_" + letter)
                else:
                    new_name.append(letter)

        return ''.join(new_name).lower()

    """
        Convert pb(.proto) to interface config file
        file_name: proto file absolute path
        api_suffix: add suffix to api name, such as suffix Public->VerifyTokenPublic
        service ProjectXX {
            rpc VerifyToken(VTRequest) returns (VTResponse) {
                option (google.api.http) = {
                    get: "/v1/verify_token"
                };
            }
        }
    """

    @classmethod
    def pb_to_interface_config(cls, file_name, output_dir, api_suffix="", interface_type=APIType.public,
                               api_list_name=None, protocol="https"):
        if not os.path.isfile(file_name) or not file_name.endswith(".proto"):
            print("Invalid file " + str(file_name))

        rpc_prefix = "    rpc "
        service_prefix = "service "
        http_method_list = ["get", "post", "delete", "put"]
        api_name_dict = {}

        with open(file_name, "r") as pb:
            line = " test"
            # 找到service开头的部分
            while line:
                line = pb.readline()
                if line.startswith(service_prefix):
                    break

            api_name_found = False
            api = None

            # 每个接口以 rcp 开头
            while line:
                line = pb.readline()
                # 找到了接口 取出接口名字
                # rpc VerifyToken(VTRequest) returns (VTResponse)
                if line.startswith(rpc_prefix) and not api_name_found:
                    api_start_index = len(rpc_prefix)
                    api_end_index = line.index("(")
                    api = line[api_start_index: api_end_index]
                    api_name_found = True
                    print(api)

                if api_name_found:
                    # 根据http method和uri 拼接interface config
                    for method in http_method_list:
                        if -1 != line.find(method + ":"):
                            uri = line.split(":")[1].replace("\n", "")
                            interface_str = "InterfaceConfig({'method': '" + method.upper() + "', 'uri': " + \
                                            uri.strip().replace("\"", "'") + "}"
                            if interface_type == APIType.internal:
                                interface_str += ", interface_type=APIType.internal"
                            if interface_type == APIType.public:
                                interface_str += ", interface_type=APIType.public"
                            interface_str += ", protocol=" + "\"" + protocol + "\""
                            interface_str += ")"
                            api_name_found = False
                            api_name_dict[api] = interface_str
                            break

        if len(api_name_dict.keys()) > 0:
            with open(output_dir + os.sep + "api_config.py", "w+") as py_file:
                py_file.write("from base.api_type import APIType\n")
                py_file.write("from base.base_func import InterfaceConfig\n")

                py_file.write("\n\nclass APINameList(object):\n")
                for api in api_name_dict.keys():
                    py_file.write("    " + api + api_suffix + " = " + "'" + api + "'" + "\n")

                py_file.write("\n\nclass APIConfig:\n")
                for api in api_name_dict.keys():
                    py_file.write("    " + api + api_suffix + " = " + api_name_dict[api] + "\n")

            if api_suffix:
                api_suffix = "_" + api_suffix.lower()

            if api_list_name:
                with open(output_dir + os.sep + "api_service.py", "w+") as py_file:
                    py_file.write("from base.base_func import BaseService\n")
                    py_file.write("from .api_config import APINameList, APIConfig\n")
                    py_file.write("from settings import TEST_ENV\n")
                    py_file.write(
                        "from .request_response import *  " +
                        " # Keep this, or [api_name + 'Request'] class wil not be found in globals()\n\n\n")

                    py_file.write("class APIService(BaseService):\n\n")
                    indent = "    "

                    py_file.write(indent + "@classmethod\n")
                    py_file.write(
                        indent + "def call_api(cls, api_name=None, request_body=None, status_success=200, " +
                        "api_config_class=APIConfig, req_class=None, res_class=None):\n")

                    py_file.write(
                        indent * 2 + "return super().call_api(req_class=globals()" +
                        "[api_name + 'Request'], res_class=globals()[api_name + 'Response'], " +
                        "api_config_class=api_config_class, env=TEST_ENV, api_name=api_name, " +
                        "request_body=request_body, status_success=status_success)\n\n")

                    for api in api_name_dict.keys():
                        py_file.write(indent + "@classmethod\n")
                        py_file.write(
                            indent + "def " + cls.get_api_name(api) + api_suffix + "(cls, request_body=None):\n")
                        py_file.write(
                            indent * 2 + "request_body = " + api + "Request" +
                            ".get_default_body() if request_body is None else request_body\n")
                        py_file.write(indent * 2 + "api_name = " + api_list_name + "." + api + "\n")
                        py_file.write(
                            indent * 2 + "ret, res = cls.call_api(api_name=api_name, request_body=request_body)\n")
                        py_file.write(indent * 2 + "return ret, res\n\n")

        else:
            print("No api is found in pb")

    """
        Convert pb(.proto) to python request response class
        file_name: proto file absolute path
    """

    @classmethod
    def pb_to_request_response(cls, file_name, output_dir, is_class_separated=False):
        if not os.path.isfile(file_name) or not file_name.endswith(".proto"):
            print("Invalid file " + str(file_name))
            return

        with open(file_name, "r") as pb:
            pb_content = pb.readlines()

        # file header
        file_header = ["# -*- coding: utf-8 -*-\n",
                       "from base.base_request import Message, BaseRequest, BaseResponse\n"]

        # get classes from pb
        class_content = []
        class_blob_dict = cls.get_class_blob_from_pb(pb_content)

        for key in class_blob_dict.keys():
            value = cls.generate_class_from_pb(class_blob_dict[key])
            class_content.extend(value)

        file_content = file_header + class_content
        if not is_class_separated:
            with open(output_dir + os.sep + "request_response.py", "w+") as py_file:
                for line in file_content:
                    py_file.write(str(line))
        else:
            # write python class to different files
            pass

    @classmethod
    def get_class_blob_from_pb(cls, pb_blob):
        blob_list = cls.get_blob_list(pb_blob)

        class_dict = {}

        for blob in blob_list:
            cls.analyze_pb_content(blob, class_dict)

        return class_dict

    @classmethod
    def generate_class_from_pb(cls, class_blob):
        pb_type_list = ["bool", "string", "bytes", "double", "float", "int32", "int64", "uint32",
                        "uint64", "sint32", "sint64", "fixed32", "fixed64", "sfixed32", "sfixed64"]

        line = class_blob[0].lstrip()
        is_enum = line.startswith("enum ")

        class_name = line.split(" ")[1]
        class_name = class_name.replace("{", "").replace("\n", "")
        class_type = "Message"
        class_body = []

        if "Request {" in line or "Request{" in line:
            class_type = "BaseRequest"
            class_body = ["\n" + 4 * " " + "def get_request(self):\n", 8 * " " + "return {\n"]

        if "Response {" in line or "Response{" in line:
            class_type = "BaseResponse"
            class_body.append(4 * " " + "schema = {\n")
            class_body.append(8 * " " + "\"type\": \"object\",\n")
            class_body.append(8 * " " + "\"title\": " + "\"The " + class_name + " Schema\",\n")
            class_body.append(8 * " " + "\"required\": [],  # write the fields which must be in response\n")
            class_body.append(8 * " " + "\"properties\": {\n")

        # write class name
        class_content = [2 * "\n" + "class " + class_name + "(" + class_type + ")" + ":\n"]

        # deal with empty response class: XXXResponse{}, which has only two line
        if 2 == len(class_blob) and line.endswith("}"):
            class_content.append(4 * " " + "pass\n")
            return class_content

        for line in class_blob[1:]:
            line = line.strip()

            if line.endswith("}"):
                break

            class_field = " " * 4 + line.replace(";", "") + "\n"

            if not is_enum:
                # separate line by space,   such as line : repeated string name = 10;
                split_list = line.split(" ")
                is_ary = False

                if "reserved" == split_list[0]:
                    continue

                if "repeated" == split_list[0]:
                    is_ary = True
                    para_filed_annotation = "repeated " + split_list[1]
                    para_type = split_list[1]
                    para_name = split_list[2]
                    para_cmt = split_list[3:]
                else:
                    para_filed_annotation = split_list[0]
                    para_type = split_list[0]
                    para_name = split_list[1]
                    para_cmt = split_list[2:]

                equator_index = para_name.find("=")
                if equator_index != -1:
                    para_name = para_name[0:equator_index]

                class_field = " " * 4 + para_name + " = \"" + para_name + "\"" + "  # " + para_filed_annotation + " "
                for cmt in para_cmt:
                    if cmt != "=":
                        class_field += " " + cmt.replace(";", "")
                class_field += "\n"

                # add get_request content for Request
                if class_type == "BaseRequest":
                    class_body.append(12 * " " + "self." + str(para_name) + ": {\n")
                    class_body.append(16 * " " + "# " + para_filed_annotation + "\n")
                    if not is_ary:
                        class_body.append(16 * " " + "'valid': '',\n")
                    else:
                        class_body.append(16 * " " + "'valid': [],\n")
                    class_body.append(16 * " " + "'invalid': []\n")
                    class_body.append(12 * " " + "},\n")

                # add schema for Response
                if class_type == "BaseResponse":
                    class_body.append(12 * " " + "\"" + para_name + "\": {\n")
                    schema_type = para_type

                    if not (para_type in pb_type_list):
                        schema_type = "object"

                    if is_ary:
                        schema_type = "array"

                    class_body.append(16 * " " + "\"type\": \"" + schema_type + "\",\n")

                    if is_ary:
                        class_body.append(16 * " " + "\"items\": [\n")
                        class_body.append(20 * " " + "{\n")
                        class_body.append(24 * " " + "\"type\": \"object\"," + "  # " + para_type + "\n")
                        class_body.append(20 * " " + "},\n")
                        class_body.append(16 * " " + "]\n")

                    class_body.append(12 * " " + "},\n")

            class_content.append(class_field)

        # add "}" for class body
        if class_type == "BaseRequest" or class_type == "BaseResponse":
            class_body.append(8 * " " + "}\n")

        if class_type == "BaseResponse":
            class_body.append(4 * " " + "}\n")

        # write class body: get_request/schema   request/response
        class_content.extend(class_body)
        return class_content

    @classmethod
    def get_blob_list(cls, pb_content):
        # get first level blob(message/enum)
        blob_list = []
        index = 0
        length = len(pb_content)

        # separate pb into blobs by keywords enum/message
        while index < length:
            line = str(pb_content[index]).lstrip()
            index += 1

            if not line.startswith("enum ") and not line.startswith("message "):
                continue

            blob_content = []
            flag_tag_count = 0
            blob_end_found = False

            # find last line of blob
            while index < length and not blob_end_found:
                # ignore empty line
                if len(line) > 1:
                    blob_content.append(line)

                if line.endswith("{\n"):
                    flag_tag_count += 1

                if line.endswith("}\n"):
                    flag_tag_count -= 1

                if flag_tag_count == 0:
                    blob_end_found = True

                if not blob_end_found:
                    line = pb_content[index].lstrip()
                    index += 1

            # add blob to blob_list
            blob_list.append(blob_content)
        return blob_list

    @classmethod
    def analyze_pb_content(cls, pb_content, class_dict):
        """
        support analyzing embedded message
        extract class from pb and save to class_dict
        pb_content must be an intact pb blob: such as
            message MapConfig {
                    int32 size = 1;
                    }
        """
        line = str(pb_content[0]).lstrip()

        if not line.startswith("enum ") and not line.startswith("message "):
            raise Exception("Not a valid class blob, first line is " + line)

        key = line
        class_dict[key] = [line]

        length = len(pb_content)
        flag_tag_count = 0
        blob_end_found = False
        line = str(pb_content[1]).lstrip()

        index = 1
        flag_tag_count += 1

        # find last line of blob
        while not blob_end_found and index < length:
            if line.startswith("enum ") or line.startswith("message "):
                skip_index = cls.analyze_pb_content(pb_content[index:], class_dict)
                index += skip_index + 1
                print("embedded class found: " + str(index) + " : " + line)
                line = pb_content[index].lstrip()
                continue

            if len(line) > 1:  # ignore empty line which contain only "\n" or "":
                class_dict[key].append(line)

            if line.endswith("{\n"):
                flag_tag_count += 1

            if line.endswith("}\n"):
                flag_tag_count -= 1

            if flag_tag_count == 0:
                blob_end_found = True
                break

            if not blob_end_found:
                index += 1
                if index < length:
                    line = pb_content[index].lstrip()

        return index

    @classmethod
    def pb2py(cls, file_name, output_dir="./services", api_suffix="", interface_type=APIType.public,
              api_list_name=None):
        cls.create_dir(output_dir)
        cls.pb_to_request_response(file_name=file_name, output_dir=output_dir)
        cls.pb_to_interface_config(file_name=file_name, output_dir=output_dir, api_suffix=api_suffix,
                                   interface_type=interface_type, api_list_name=api_list_name, protocol="https")


if __name__ == '__main__':
    file = "../project/example/pb.proto"
    Util.pb2py(file, output_dir="../project/example/services", api_suffix="", interface_type=APIType.internal,
               api_list_name="APINameList")
