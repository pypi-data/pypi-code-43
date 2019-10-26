from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class VpcTemplate(core.Stack):
    """
    Template class which creates a highly opinionated VPC structure.
    """
    STACK_NAME_SUFFIX = 'VpcStack'

    def __init__(self, prefix: str, scope: core.Construct, **kwargs) -> None:
        """
        Constructor.

        :param prefix: Prefix for the resource names.
        :param scope: AWS CDK specific construct scope.
        :param kwargs: Other arguments.
        """
        stack_name = prefix + self.STACK_NAME_SUFFIX

        super().__init__(scope, stack_name, **kwargs)

        self.__vpc = ec2.Vpc(
            self,
            'Vpc',
            # The 'cidr' parameter configures the IP range and size of the entire VPC.
            # The IP space will be divided over the configured subnets.
            cidr='10.0.0.0/16',
            # The 'maxAzs' parameter configures the maximum number of availability zones to use.
            max_azs=3,
            # The number of NAT Gateways to create. For example, if set this to 1 and your subnet
            # configuration is for 3 Public subnets then only one of the Public subnets will have
            # a gateway and all Private subnets will route to this NAT Gateway
            nat_gateways=1,
            # The 'subnetConfiguration' parameter specifies the "subnet groups" to create.
            # Every subnet group will have a subnet for each AZ, so this
            # configuration will create `3 groups × 3 AZs = 9` subnets.
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=prefix + 'SubnetPublic',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=22,

                ),
                ec2.SubnetConfiguration(
                    name=prefix + 'SubnetPrivate',
                    subnet_type=ec2.SubnetType.PRIVATE,
                    cidr_mask=22,

                ),
                ec2.SubnetConfiguration(
                    name=prefix + 'SubnetIsolated',
                    subnet_type=ec2.SubnetType.ISOLATED,
                    cidr_mask=22,

                )
            ]
        )

    @property
    def vpc(self) -> ec2.Vpc:
        """
        AWS VPC property.

        :return: Returns AWS VPC instance.
        """
        return self.__vpc
