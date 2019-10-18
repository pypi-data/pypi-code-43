from dotenv import load_dotenv

load_dotenv()

import os

os.environ.setdefault('SIMPLE_SETTINGS', 'itkdb.settings.base')
from simple_settings import settings

__all__ = ['settings']
