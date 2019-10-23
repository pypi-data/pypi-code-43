import os
from enum import Enum
from pathlib import Path
from typing import List, Any, Callable, Optional

from django.core.management.utils import get_random_secret_key


env: Callable[[str, Optional[Any]], str] = os.environ.get


def get(name: str, default: Any = None) -> Any:
    return os.environ.get(name, default)


def get_bool(name: str, default: bool = False) -> bool:
    true_values = [True, 'true']
    if env(name) is None:
        return default
    else:
        return env(name).lower() in true_values


def get_or_create_secret_key(base_dir: str, file_name: str = '.secret_key') -> str:
    key_file_path: str = os.path.join(base_dir, file_name)
    try:
        return Path(key_file_path).read_text()
    except (ImportError, FileNotFoundError):
        secret_key = get_random_secret_key()
        Path(key_file_path).write_text(secret_key)
        
        return Path(key_file_path).read_text()


def allowed_hosts() -> List[str]:
    if env('DJANGO_ALLOWED_HOSTS_STRING'):
        return str(env('DJANGO_ALLOWED_HOSTS_STRING')).strip('"').split()
    elif is_debug():
        return ['*']
    else:
        return ["127.0.0.1", "0.0.0.0", 'localhost']


class DjangoEnv(Enum):
    DEV = 'dev'
    STAGE = 'stage'
    PROD = 'prod'


def is_dev() -> bool:
    return env('DJANGO_ENV', default=DjangoEnv.DEV.value) == DjangoEnv.DEV.value


def is_prod() -> bool:
    return env('DJANGO_ENV') == DjangoEnv.PROD.value


def is_stage() -> bool:
    return env('DJANGO_ENV') == DjangoEnv.STAGE.value


def django_env() -> DjangoEnv:
    if is_stage():
        return DjangoEnv.STAGE
    elif is_prod():
        return DjangoEnv.PROD
    else:
        return DjangoEnv.DEV


def is_debug() -> bool:
    if env('IS_DJANGO_DEBUG') is None:
        django_env_value: DjangoEnv = django_env()
        if django_env_value is DjangoEnv.DEV:
            return True
    else:
        return get_bool('IS_DJANGO_DEBUG') or get_bool('DJANGO_DEBUG')
