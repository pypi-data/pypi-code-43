import os
import tempfile
import threading
import time

from shield34_reporter.auth.sdk_authentication import SdkAuthentication
from shield34_reporter.listeners.listener_utils import ListenerUtils
from shield34_reporter.model.contracts.run_contract import RunContract
from shield34_reporter.model.csv_rows.general_csv_row import GeneralCsvRow
from .block_run_report_container import BlockRunReportContainer
from shield34_reporter.utils.time_utils import TimeUtils


class RunReportContainer():
    threadlocal = threading.local()
    runContract = None

    @staticmethod
    def get_current_block_run_holder():

        run_contract = RunReportContainer.get_current_run_contract()
        if run_contract.runName == "" or run_contract.id == "":
            run_contract = ListenerUtils.save_or_update_run(run_contract)
        if not hasattr(RunReportContainer.threadlocal, 'blockRunReportContainer'):
            block_run_report_container = BlockRunReportContainer()
            block_run_report_container.blockRunContract.runContract = run_contract
            RunReportContainer.threadlocal.blockRunReportContainer = block_run_report_container
        else:
            block_run_report_container_save_in_thread = getattr(RunReportContainer.threadlocal, 'blockRunReportContainer')
            if block_run_report_container_save_in_thread is None:
                block_run_report_container = BlockRunReportContainer()
                block_run_report_container.blockRunContract.runContract = run_contract
                RunReportContainer.threadlocal.blockRunReportContainer = block_run_report_container

        return getattr(RunReportContainer.threadlocal, 'blockRunReportContainer')

    @staticmethod
    def get_reports_folder_path():
        temp_directory = tempfile.gettempdir()
        return temp_directory

    @staticmethod
    def get_current_run_contract():
        if RunReportContainer.runContract is None:
            RunReportContainer.runContract = RunReportContainer.create_current_run_contract("Main suite")

        return RunReportContainer.runContract

    @staticmethod
    def create_current_run_contract(parent_suite_name):
        if RunReportContainer.runContract is None :
            RunReportContainer.runContract = RunContract(parent_suite_name, 0, TimeUtils.get_current_timestamp())
            RunReportContainer.set_run_contract(ListenerUtils.save_or_update_run(RunReportContainer.runContract))

        return RunReportContainer.runContract

    @staticmethod
    def set_run_contract(run_contract_to_save):
        RunReportContainer.runContract.id = run_contract_to_save.id
        RunReportContainer.runContract.startTimestamp = run_contract_to_save.startTimestamp
        RunReportContainer.runContract.runName = run_contract_to_save.runName
        RunReportContainer.runContract.index = run_contract_to_save.index

    @staticmethod
    def add_report_csv_row(csv_row):
        if not SdkAuthentication.isAuthorized:
            return

        if isinstance(csv_row, GeneralCsvRow):
            RunReportContainer.get_current_block_run_holder().generalReport = csv_row

        else:
            RunReportContainer.get_current_block_run_holder().blockReport.append(csv_row)

