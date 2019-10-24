import os
from concurrent.futures.thread import ThreadPoolExecutor

from shield34_reporter.model.contracts.block_contract import BlockContract
from shield34_reporter.model.contracts.block_run_contract import BlockRunContract
from shield34_reporter.model.enums.block_type import BlockType
from shield34_reporter.model.enums.status import Status


class BlockRunReportContainer:
    blockReport = []
    generalReport = None
    blockRunContract = None
    currentDriver = None
    currentBlockFolderPath = ""
    pool = ThreadPoolExecutor(10)
    webElements = {}
    proxyServer = None

    def __init__(self):
        self.blockRunContract = BlockRunContract(Status.PENDING, 0, 0, "", "", "", "", "", BlockContract(BlockType.UNKNOWN, "", "", 1, "", "", ""))

    def reset_block_run_contract(self):
        self.blockRunContract = BlockRunContract(Status.PENDING, 0, 0, "", "", "", "", "", BlockContract(BlockType.UNKNOWN, "", "", 1, "", "", ""))
        self.currentBlockFolderPath = ""
        self.blockReport = []
        self.generalReport = None

    def set_block_run_contract(self, block_run_contract):
        self.blockRunContract = block_run_contract
        self.blockRunContract.blockContract = block_run_contract.blockContract

    def generate_current_block_folder_path(self):
        from shield34_reporter.container.run_report_container import RunReportContainer
        file_name = os.path.join(RunReportContainer.get_reports_folder_path(), "Shield34-report", "run_" + self.blockRunContract.runContract['id'], "block_run_" + self.blockRunContract.id)
        os.makedirs(file_name)
        return file_name

    def get_current_test_folder(self):
        if self.currentBlockFolderPath == "" :
            self.currentBlockFolderPath = self.generate_current_block_folder_path()
        return self.currentBlockFolderPath

    def shut_down_executor(self):
        self.pool.shutdown(True)

    def reset_executor(self):
        self.pool = ThreadPoolExecutor(10)

    def add_web_element(self, id, locator):
        self.webElements[id] = locator

    def get_web_element(self, id):
        return self.webElements[id]
