class S3FileDetails:
    runId = ""
    blockRunId = ""
    fileName = ""
    fileType = None

    def __init__(self, run_id, block_run_id, file_name, file_type):
        self.runId = run_id
        self.blockRunId = block_run_id
        self.fileName = file_name
        self.fileType = file_type