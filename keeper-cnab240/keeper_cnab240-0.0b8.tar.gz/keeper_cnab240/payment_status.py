class StatusModel:
    is_error = None
    is_processed = None
    is_income = None
    is_info = None
    is_outcome = None
    is_reverted = None
    message = None

    def __init__(self, processed: bool, move: str, message: str = None):
        self.is_error = not processed
        self.is_processed = processed
        self.is_income = move == 'in' or move == 'revert'
        self.is_info = move == 'info'
        self.is_outcome = move == 'out'
        self.is_reverted = move == 'revert'
        self.error_type = message if self.is_error else None
        self.message = message

    def __str__(self):
        return '<StatusModel is_error={} is_processed={} is_income={} is_info={} is_outcome={} ' \
               'is_reverted={} error_type={} message={}>'.format(self.is_error,
                                                                 self.is_processed,
                                                                 self.is_income,
                                                                 self.is_info,
                                                                 self.is_outcome,
                                                                 self.is_reverted,
                                                                 self.error_type,
                                                                 self.message)
