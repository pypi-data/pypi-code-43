import os

from lib import P4InfoHelper


class LoadConfig:

    def __init__(self, client, args):
        self.client = client
        self.args = args

    def load_config(self):
        pipeline_id = self.args.pipeline_id
        p4info_file_path = self.args.p4info_path
        config_file_path = self.args.config_path

        if not os.path.isfile(p4info_file_path):
            raise Exception("Not a valid filename of p4info")

        if not os.path.isfile(config_file_path):
            raise Exception("Not a valid filename of device config")

        print "Loading new config"

        p4info = P4InfoHelper.read_from_file(p4info_file_path)
        p4info_helper = P4InfoHelper(p4info)

        self.client.set_forwarding_pipeline_config_request(
            pipeline_id=pipeline_id,
            p4info=p4info_helper.p4info,
            config_file_path=config_file_path
        )

        print "Config loaded successfully"
