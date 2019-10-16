from QiDataProcessing.Core.EnumBarType import EnumBarType


class BarProviderInfo:
    def __init__(self):
        self.time_slices = []
        self.offset = 0
        self.living_time = None
        self.interval = 0
        self.bar_type = EnumBarType.minute
