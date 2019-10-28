import persistent


class ForwardingPipelineConfig(persistent.Persistent):

    def __init__(self, device_config, p4info):
        self.device_config = device_config
        self.p4info = p4info

    def update_device_config(self, device_config):
        self.device_config = device_config

    def update_p4info(self, p4info):
        self.p4info = p4info

    def __str__(self):
        return "ForwardingPipelineConfig(filepath=%s,\n" \
               "P4Info: %s" % (self.device_config, self.p4info)

