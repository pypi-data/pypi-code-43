import kpc_nifi_utils.shared.constants as constants
from kpc_nifi_utils.common.args_parser import Args


class AwsArgs(Args):
    def __init__(self, *args):
        super().__init__(*args)

    def get_key(self):
        return self.get(constants.AWS_KEY)

    def get_secret(self):
        return self.get(constants.AWS_SECRET)
