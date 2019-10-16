# --- Standard Library Imports ------------------------------------------------
from pathlib import Path
import functools

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
from rtm.containers.fields import Fields
import rtm.main.context_managers as context
from rtm.containers.worksheet_columns import WorksheetColumns
from rtm.containers.work_items import WorkItems
import rtm.main.excel as excel


# --- Worksheet Path ----------------------------------------------------------
@functools.lru_cache()
def get_rtm_path():
    return Path(__file__).parent / "test_rtm.xlsx"


@pytest.fixture(scope="session")
def fix_path() -> Path:
    return get_rtm_path()


# --- Worksheet Columns -------------------------------------------------------
@functools.lru_cache()
def get_worksheet_columns(worksheet_name):
    path = get_rtm_path()
    wb = excel.get_workbook(path)
    ws = excel.get_worksheet(wb, worksheet_name)
    return WorksheetColumns(ws)


@pytest.fixture(scope="session")
def fix_worksheet_columns():
    return get_worksheet_columns


# --- Fields ------------------------------------------------------------------
@functools.lru_cache()
def get_fields(worksheet_name):
    with context.worksheet_columns.set(get_worksheet_columns(worksheet_name)):
        return Fields()


@pytest.fixture(scope="function")
def fix_fields():
    return get_fields


# --- Work Items --------------------------------------------------------------
@functools.lru_cache()
def get_work_items(worksheet_name):
    with context.fields.set(get_fields(worksheet_name)):
        return WorkItems()


@pytest.fixture(scope="function")
def fix_work_items():
    return get_work_items
