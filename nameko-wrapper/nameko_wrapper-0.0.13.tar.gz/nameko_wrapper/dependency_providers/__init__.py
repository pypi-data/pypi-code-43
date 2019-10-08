"""
Nameko Dependencies
"""

# 兼容0.0.7之前版本, 后续版本应避免在此文件添加依赖注入
from nameko_wrapper.elasticsearch.dependency_providers import ElasticSearch
from .crontab import CrontabDependency
from .logger import LoggerDependency
