import configparser
import os

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
    def get_default_params(options):
        """
        获取配置文件信息
        :param options:
        :return:
        """
        config = ConfigParser.get_config_parser()
        section = 'section = "DefaultParams"'

        config.read(os.path.dirname(os.path.dirname(__file__)) + os.sep + 'config.ini')
        if options in config.options(section):
            return config[section][options]

    @staticmethod
    def set_default_params(options, value):
        """
        编辑配置文件
        :param options: 要编辑的key
        :param value:
        :return:
        """
        config = ConfigParser.get_config_parser()

        section = 'DefaultParams'

        file_path = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'config.ini'
        config.read(file_path)
        config.set(section, options, value)
        with open(file_path, "w") as f:
            config.write(f)
