from p4.v1.p4runtime_pb2 import GetForwardingPipelineConfigRequest


class GetConfig:

    def __init__(self, client, args):
        self.client = client
        self.args = args

    def get_config(self):
        pipeline_id = self.args.pipeline_id
        response_type = self.args.response_type
        p4info_file_path = self.args.p4info_path
        config_file_path = self.args.config_path

        config = self.client.get_forwarding_pipeline_config_request(pipeline_id=pipeline_id, response_type=response_type)

        device_config = config.p4_device_config
        p4info = config.p4info

        p4info_status = False
        response_type_enum = GetForwardingPipelineConfigRequest.ResponseType.DESCRIPTOR.values_by_name[response_type]
        if response_type_enum.number == GetForwardingPipelineConfigRequest.ALL or response_type_enum.number == GetForwardingPipelineConfigRequest.P4INFO_AND_COOKIE:
            if str(p4info):
                with open(p4info_file_path, "w") as p4info_f:
                    p4info_f.write(str(p4info))

                print "P4Info saved successfully in ", p4info_file_path
                p4info_status = True
            else:
                print "P4Info is empty!"

        if response_type_enum.number == GetForwardingPipelineConfigRequest.ALL or response_type_enum.number == GetForwardingPipelineConfigRequest.DEVICE_CONFIG_AND_COOKIE:
            if device_config:
                with open(config_file_path, "w") as config_f:
                    config_f.write(device_config)

                print "Device config saved successfully in l", config_file_path
            else:
                print "Device config is empty!"

        return p4info_status
