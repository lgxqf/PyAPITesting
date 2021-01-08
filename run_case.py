# -*- coding: utf-8 -*-
import datetime
import logging
import os

from base.base_func import *
from base.util import get_log_path
from settings import project_root

RESULT_DIR = "test_results"


def run_case(host, path_list, project_name, stop_if_failure, dummy_run, log, **kwargs):
    error_cases = {}
    ok_cases = {}
    pass_case_list = []
    fail_cases = {}
    doc_dict = {}
    case_count = 0
    no_doc_case = []
    begin_time = datetime.datetime.now()
    result_file_name = RESULT_DIR + os.sep + 'result_' + time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime()) + '.txt'

    error_found = False

    with open(result_file_name, 'a') as result_file:
        result_file.write(str(time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime())))
        result_file.flush()

        # support file and directory
        for case_path in path_list:
            case_file = []

            if error_found and stop_if_failure:
                break

            if os.path.isfile(case_path) and case_path.endswith(".py"):
                case_file.append(case_path)
            else:
                for r, d, f in os.walk(case_path):
                    for item in f:
                        if item.endswith('.py') and '__init__' not in item:
                            case_file.append(os.path.join(r, item))

            for test_case in case_file:
                func = test_case.split(os.path.sep)[-1].replace('.py', '')
                flow_flag = False
                func_name_flag = False
                func_name = "def " + func + "("
                case_count += 1

                with open(test_case, errors='ignore') as f:
                    for line in f.readlines():
                        if line.startswith('@flow'):
                            flow_flag = True

                        if func_name in line:
                            func_name_flag = True

                        if flow_flag and func_name_flag:
                            break

                if not (flow_flag and func_name_flag):
                    log.info('[error]' + str(test_case) + 'do not have @flow or function name : ' + str(func_name))
                    error_cases[test_case] = "No @flow or function_name: " + func_name
                    continue

                case_import_path = test_case[test_case.index(project_name) + len(project_name) + 1:]
                module = case_import_path.replace(os.path.sep, '.').replace('.py', '')
                dd = __import__(module, fromlist=[func])
                fun = getattr(dd, func, None)
                log.info("\n=================================================Running case " + test_case + "\n")
                ret = [{"result": "fail", "name": test_case}]
                doc = fun.__doc__

                try:
                    if not doc:
                        no_doc_case.append(func)

                    if doc in doc_dict.keys():
                        doc_dict[doc]['count'] += 1
                        doc_dict[doc]['case_file'].append(test_case)
                    else:
                        doc_dict[doc] = {"count": 1, "case_file": [test_case]}

                    if not dummy_run:
                        kwargs.update(host)
                        ret = fun(kwargs, log=log)
                    else:
                        ret = [{"result": "pass", "name": test_case}]

                except Exception as e:
                    ret = [{"result": "fail", "exception": e}]
                    log.info(str(traceback.format_exc()))

                finally:
                    log.info(ret)

                    if ret and ret[0]['result'].lower() == 'pass':
                        ok_cases[test_case] = ret
                        ret = ret[0]
                        value = '{: <6}'.format(str(case_count))
                        value += '{: <60}'.format((ret['name']))
                        value += "\n"
                        pass_case_list.append(value)
                    else:
                        fail_cases[test_case] = ret

                        ret = ret[0]
                        value = '{: <6}'.format(str(case_count))
                        value += '{: <60}'.format(str(ret['name']))
                        value += " " * 4
                        response = ret.get('response')
                        reason = ret.get('reason')

                        if reason:
                            value += str(reason)

                        if response:
                            value += str(response)

                        # result_file.write(value + "\n")
                        result_file.flush()

                        if stop_if_failure:
                            error_found = True
                            break

    end_time = datetime.datetime.now()

    # wait till all the test log are output in console
    time.sleep(3)

    log.info("\n" * 2 + "=" * 20 + "Test report" + "=" * 20)
    if len(ok_cases) != 0:
        log.info("\n\nPass " + str(len(ok_cases)))
        for key in ok_cases:
            log.info(key + "     " + str(ok_cases[key]))

    if len(fail_cases) != 0:
        log.info("\n\nFail " + str(len(fail_cases)))
        for key in fail_cases:
            log.info(key + "     " + str(fail_cases[key]))

    printed = False

    for key in doc_dict.keys():
        count = doc_dict[key]['count']
        if count > 1:
            if not printed:
                log.error("!!!ERROR More than 1 case have same __doc__")
                printed = True
            log.info(str(count) + "    " + str(key))
            for item in doc_dict[key]['case_file']:
                log.info(item)

    if len(error_cases) != 0:
        log.info("\n" + str(len(error_cases)) + " Error!!!" + " No @flow or function_name")
        for key in error_cases:
            log.info(str(key) + str(error_cases[key]))

    if len(no_doc_case) != 0:
        log.info("\n" + str(len(no_doc_case)) + " Warning!!! " + " Following cases have not doc")
        for no_title_case in no_doc_case:
            log.info(no_title_case)

    used_time = str(end_time - begin_time)

    with open(result_file_name, 'a') as result_file:
        if len(pass_case_list) > 0:
            result_file.write(2 * "\n")
            result_file.write("Pass case list: " + "\n")

            for pass_case in pass_case_list:
                result_file.write(str(pass_case) + "\n")
                result_file.flush()

        if len(fail_cases) > 0:
            result_file.write(2 * "\n")
            result_file.write("Failed case list: " + "\n")

            for failed_case in fail_cases:
                result_file.write(str(failed_case) + "\n")
                result_file.flush()

        result_list = ["\n" * 2 + 20 * "=" + "Test result" + 20 * "=", "Totally " + str(case_count) + " cases",
                       "Available " + str(case_count - len(error_cases)), "Pass " + str(len(ok_cases)),
                       "Fail " + str(len(fail_cases)), "Error " + str(len(error_cases)),
                       "Time " + str(used_time[0: used_time.index(".")])]

        for item in result_list:
            log.info(item)
            result_file.write(item + "\n")
            result_file.flush()


if __name__ == '__main__':

    log = log_config(c_level=logging.DEBUG, f_level=logging.DEBUG, out_path=get_log_path())[0]

    project = 'example'

    # 用例的根目录
    case_home_path = os.path.abspath('.') + os.sep + 'project' + os.sep + project + os.sep + 'cases'

    # 测试用例列表
    case_total_list = [
        'module',
    ]

    # 只检查文件合法性，如是否有@flow, 是否文件名和函数名一样
    run_in_dummy_mode = False

    # 运行用例失败时即可停止，设为True方便调试失败用例
    if_failure_stop = False

    # 回归测试时，此项必须为True
    regression_test = False

    for index, case in enumerate(case_total_list):
        case_total_list[index] = case_home_path + os.sep + case
        log.info(case_total_list[index])

    # 循环执行次数
    loop = 1

    while loop >= 1:
        run_case({"host": "0.0.0.0"}, case_total_list, project_root, if_failure_stop, run_in_dummy_mode, log)
        loop -= 1
