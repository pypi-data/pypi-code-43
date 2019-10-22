from shield34_reporter.model.contracts.block_contract import BlockContract
from shield34_reporter.model.contracts.run_contract import RunContract
from shield34_reporter.model.enums.status import Status


class BlockRunContract:
    status = Status.PENDING
    startTimestamp = 0
    endTimestamp = 0
    reportFilePath = ""
    browserDetails = ""
    windowResolution = ""
    driverDetails = ""
    osType = ""
    blockContract = BlockContract()
    runContract = RunContract()
    id = ""


    def __init__(self, status, start_timestamp, end_timestamp, report_file_path, browser_details, window_resolution, driver_details, os_type, block_contract, run_contract=RunContract(), id=""):
        self.status = status
        self.startTimestamp = start_timestamp
        self.endTimestamp = end_timestamp
        self.reportFilePath = report_file_path
        self.browserDetails = browser_details
        self.windowResolution = window_resolution
        self.driverDetails = driver_details
        self.osType = os_type
        self.blockContract = block_contract
        self.runContract = run_contract
        self.id = id

