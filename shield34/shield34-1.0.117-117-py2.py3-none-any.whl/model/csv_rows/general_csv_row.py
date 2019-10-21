from shield34_reporter.model.csv_rows.basic_csv_row import BasicCsvRow


class GeneralCsvRow(BasicCsvRow):
    runId = ""
    blockId = ""
    parentSuiteName = ""
    runStartTimestamp = ""
    testStartTimestamp = ""
    suiteName = ""
    testClassName = ""
    testName = ""
    testParams = {}

    def __init__(self, run_id, block_id, parent_suite_name, run_start_timestamp, test_start_timestamp, suite_name, test_class_name, test_name, test_params):
        self.runId = run_id
        self.blockId = block_id
        self.parentSuiteName = parent_suite_name
        self.runStartTimestamp = run_start_timestamp
        self.testStartTimestamp = test_start_timestamp
        self.suiteName = suite_name
        self.testClassName = test_class_name
        self.testName = test_name
        self.testParams = test_params
        super(GeneralCsvRow, self).__init__([{"timestamp", "run_id", "block_id", "parent_suite_name", "run_start_timestamp", "test_start_timestamp", "suite_name", "test_class_name", "test_name" "test_params"}], "general.csv")

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), self.runId, self.blockId, self.parentSuiteName, str(int(round(self.runStartTimestamp * 1000.))), str(int(round(self.testStartTimestamp * 1000.))), self.suiteName, self.testClassName, self.testName, self.testParams]

