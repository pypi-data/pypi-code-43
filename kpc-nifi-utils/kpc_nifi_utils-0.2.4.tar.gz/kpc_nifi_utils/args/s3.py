from kpc_nifi_utils.args.aws import AwsArgs
from kpc_nifi_utils.shared import constants


class S3Args(AwsArgs):
    def __init__(self, *args):
        super().__init__(*args)

    def get_bucket(self):
        return self.get(constants.AWS_S3_BUCKET)
