import logging
import configparser
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


def get_log_path(dir_name='log'):
    cwd = os.path.dirname(os.path.realpath(__file__))
    dir_index = cwd.rindex(project_root)
    log_path = cwd[: dir_index + len(project_root)] + os.sep + 'test_results' + os.sep + dir_name
    return log_path


def get_random_len(data_len=128, data_type=int, r_float=1):
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


def get_project_path(cls, dir_name=None):
    cwd = os.path.dirname(os.path.realpath(__file__))

    root_name = project_root
    dir_index = cwd.rindex(root_name)
    return cwd[: dir_index + len(root_name)] + os.sep + dir_name


class Util:
    """
        Convert pb(.proto) to interface config file
        file_name: proto file absolute path

        service ProjectXX {
            rpc VerifyToken(VTRequest) returns (VTResponse) {
                option (google.api.http) = {
                    get: "/v1/verify_token"
                };
            }
        }
    """

    @classmethod
    def pb_to_interface_config(cls, file_name, interface_type=APIType.internal):
        if not os.path.isfile(file_name) or not file_name.endswith(".proto"):
            print("Invalid file " + str(file_name))

        rpc_prefix = "    rpc "
        service_prefix = "service "
        http_method_list = ["put", "post", "delete", "put"]
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
                    # 根据http method和 uir 拼接interface config
                    # get: "/v1/verify_token"
                    # VerifyToken = InterfaceConfig({'method':'POST:','uri':' "/v1/authorization_internal"'}, interface_type=APIType.internal)
                    for method in http_method_list:
                        if -1 != line.find(method + ":"):
                            uri = line.split(":")[1].replace("\n", "")
                            interface_str = "InterfaceConfig({'method': '" + method.upper() + "', 'uri': " + "'" + uri + "'}"
                            if interface_type == APIType.internal:
                                interface_str += ", interface_type=APIType.internal"
                            if interface_type == APIType.public:
                                interface_str += ", interface_type=APIType.public"
                            interface_str += ")"
                            api_name_found = False
                            api_name_dict[api] = interface_str
                            break

        if len(api_name_dict.keys()) > 0:
            with open("../api_config_internal.py", "w+") as py_file:
                py_file.write("from base.api_type import APIType\n")
                py_file.write("from base.base_func import InterfaceConfig\n")

                py_file.write("\n\nclass APINameList(object):\n")
                for api in api_name_dict.keys():
                    py_file.write("    " + api + " = " + "'" + api + "'" + "\n")

                py_file.write("\n\nclass APIConfig:\n")
                for api in api_name_dict.keys():
                    py_file.write("    " + api + " = " + api_name_dict[api] + "\n")

        else:
            print("No api is found in pb")

    """
        Convert pb(.proto) to python request response class
        file_name: proto file absolute path
    """

    @classmethod
    def pb_to_py(cls, file_name):
        if not os.path.isfile(file_name) or not file_name.endswith(".proto"):
            print("Invalid file " + str(file_name))

        class_name_list = []
        line = "test"

        with open("pb.py", "w+") as py_file:
            py_file.write("from common_service.base_request import Message, BaseRequest, BaseResponse\n")
            with open(file_name, "r") as pb:

                while line:
                    line = pb.readline()

                    # class found in pb
                    is_enum = line.startswith("enum ")
                    is_message = line.startswith("message ")

                    if not is_enum and not is_message:
                        continue

                    class_name = line.split(" ")[1]
                    class_name_list.append(class_name)
                    class_type = "Message"

                    if "Request {" in line:
                        class_type = "BaseRequest"

                    if "Response {" in line:
                        class_type = "BaseResponse"

                    # write class name
                    value = 2 * "\n" + "class " + class_name + "(" + class_type + ")" + ":\n"
                    py_file.write(value)
                    py_file.flush()
                    strip_line = pb.readline().strip()

                    if strip_line.endswith("}"):
                        py_file.write(4 * " " + "pass\n")
                        continue

                    get_request_str = ["\n" + 4 * " " + "def get_request(self):\n", 8 * " " + "return {\n"]

                    # end of class mark definition is }
                    while not strip_line.endswith("}") and line:
                        if strip_line.startswith("//") or not strip_line:
                            strip_line = pb.readline().strip()
                            continue

                        content = " " * 4 + strip_line.replace(";", "") + "\n"

                        if not is_enum:
                            split_list = strip_line.split(" ")

                            if "repeated" == split_list[0]:
                                para_type = "repeated " + split_list[1]
                                para_name = split_list[2]
                                para_cmt = split_list[3:]
                            else:
                                para_type = split_list[0]
                                para_name = split_list[1]
                                para_cmt = split_list[2:]

                            content = " " * 4 + para_name + " = \"" + para_name + "\"" + "  # " + para_type + " "
                            for cmt in para_cmt:
                                if cmt != "=":
                                    content += cmt.replace(";", "")
                            content += "\n"

                            get_request_str.append(12 * " " + "self." + str(para_name) + ": {\n")
                            get_request_str.append(16 * " " + "# " + para_type + "\n")
                            get_request_str.append(16 * " " + "'valid': '',\n")
                            get_request_str.append(16 * " " + "'invalid': ''\n")
                            get_request_str.append(12 * " " + "},\n")

                        py_file.write(content)
                        strip_line = pb.readline().strip()
                        print(strip_line)

                    get_request_str.append(8 * " " + "}\n")

                    if len(get_request_str) > 3:
                        for content in get_request_str:
                            py_file.write(content)

    """
        Add ID and Project field for test case file
        project_name: project name
        path_list: case directory list
    """

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
                case_title = str(test_case.split(os.path.sep)[-1].replace('.py', ''))

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
    def get_project_home(cls):
        cwd = os.path.dirname(os.path.realpath(__file__))
        dir_index = cwd.rindex(project_root)
        return cwd[: dir_index + len(project_root)]


class ConfigParser:

    @staticmethod
    def get_config_parser():
        """
        实例化一个ConfigParser
        :return:
        """
        config = configparser.ConfigParser()
        return config

    @staticmethod
    def get_default_params(options, project='gateway'):
        """
        获取配置文件信息
        :param options:
        :param project:
        :return:
        """
        config = ConfigParser.get_config_parser()

        section = ''
        if project == "gateway":
            section = "DefaultParams"
        elif project == "tianshu":
            section = "DefaultParamsTS"
        config.read(os.path.dirname(os.path.dirname(__file__)) + os.sep + 'config.ini')
        if options in config.options(section):
            return config[section][options]

    @staticmethod
    def set_default_params(options, value, project='gateway'):
        """
        编辑配置文件
        :param options: 要编辑的key
        :param value:
        :param project:
        :return:
        """
        config = ConfigParser.get_config_parser()

        section = ''
        if project == "gateway":
            section = "DefaultParams"
        elif project == "tianshu":
            section = "DefaultParamsTS"

        file_path = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'config.ini'
        config.read(file_path)
        config.set(section, options, value)
        with open(file_path, "w") as f:
            config.write(f)


if __name__ == '__main__':
    Util.pb_to_interface_config("/Users/mayi/Project/PyAPITesting/x.proto")
