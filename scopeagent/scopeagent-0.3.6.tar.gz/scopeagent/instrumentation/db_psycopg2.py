from .sql.psycopg2 import install_patches
from . import run_once


@run_once
def patch(tracer):
    install_patches(tracer)
