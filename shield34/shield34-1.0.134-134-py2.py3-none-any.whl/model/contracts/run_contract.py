class RunContract(object):
    id = ''
    runName = ""
    index = 0
    startTimestamp = 0

    def __init__(self, run_name="", index=0, start_timestamp=0, id=''):
        self.id = id
        self.runName = run_name
        self.index = index
        self.startTimestamp = start_timestamp

    def reprJSON(self):
        return dict(id=self.id, runName=self.runName, index=self.index, startTimestamp=self.startTimestamp)


def make_run_contract(run_name, index, start_timestamp):
    run_contract = RunContract(run_name, index, start_timestamp)
    return run_contract

