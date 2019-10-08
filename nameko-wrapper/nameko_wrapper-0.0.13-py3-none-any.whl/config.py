"""
Nameko Config
"""
from nameko.cli.main import setup_parser
from nameko import constants
import os

import yaml


def find_config_file(dirname=None, prefix=None, *, level=None):
    """
    Find config file path - Only find execute dir parent and current dir
    以项目服务执行目录开始继续向上查找

    :param dirname: 配置文件目录名
    :param prefix: 配置文件模式 dev/test/prod
    :param level: 发现级数
    """
    dirname = dirname if dirname else 'config'
    prefix = prefix if prefix else 'dev'
    level = level if isinstance(level, int) and level > 0 else 5
    current_dir = os.path.abspath(os.path.curdir)

    def find_current_dir(path):
        dirs = (f for f in os.listdir(path) if f == dirname and os.path.isdir(os.path.join(path, f)))
        for d in dirs:
            cd = os.path.join(path, d)
            files = [
                cf for cf in os.listdir(cd)
                if cf.startswith(prefix) and cf.endswith(('yml', 'yaml')) and os.path.isfile(os.path.join(cd, cf))
            ]
            if len(files) == 1:
                return os.path.join(cd, files[0])
            elif len(files) > 1:
                raise EnvironmentError('Find multiple setting yaml file by find rule. {}'.format(files))
            else:
                return None

    find_path = current_dir
    while level > 0:
        level -= 1
        result = find_current_dir(find_path)
        if result:
            return result
        else:
            # find up
            parend_dir = os.path.dirname(find_path)
            if parend_dir == find_path:
                return None
            else:
                find_path = parend_dir
    else:
        return None


# 解析配置文件
def get_config(config_file_path=None, *, dirname=None, prefix=None, level=None):
    """
    获取配置文件
    :param config_file_path: 当指定config file path时，获取config file path的配置文件，否则默认获取命令行配置文件路径
    :param dirname
    :param prefix
    :param level
    :return: 配置字典
    """
    # 合并默认参数
    DEFAULT_PARAMS = {
        constants.AMQP_URI_CONFIG_KEY: 'broker'
    }
    config = {}

    if config_file_path:
        f = open(config_file_path, 'rt')
    else:
        # 通过nameko命令行参数获取配置文件信息
        parser = setup_parser()
        args = parser.parse_args()
        # 获取默认参数值
        for param, key in DEFAULT_PARAMS.items():
            if hasattr(args, key):
                config[param] = getattr(args, key)

        if getattr(args, 'config', None):
            f = open(args.config, 'rt')
        else:
            file = find_config_file(dirname, prefix, level=level)
            if file:
                f = open(file, 'rt')
            else:
                raise FileNotFoundError('Setting yaml file does not found.')

    c = yaml.safe_load(f)
    f.close()

    config.update(c)
    return config


# YAML 配置文件配置
yaml_config = get_config()


class Config(object):
    """Yaml Configure"""

    def __init__(self, path=None, *, dirname=None, prefix=None, level=None, refresh=False):
        """读取配置文件"""
        # 此处为了避免每次获取配置故改为这种结构

        if refresh or path:
            self._config = get_config(path, dirname=dirname, prefix=prefix, level=level)
        else:
            self._config = yaml_config

    def __getattr__(self, item):
        return self._config[item]

    def __getitem__(self, item):
        return self._config[item]

    def to_dict(self):
        return self._config

    @property
    def params(self):
        return self._config.keys()



# 常用的配置获取
config = Config()
amqp_config = {
    'AMQP_URI': config['AMQP_URI']
}

es_config = config['ELASTICSEARCH']['HOSTS']
