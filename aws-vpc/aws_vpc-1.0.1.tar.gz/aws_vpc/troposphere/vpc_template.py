from typing import Dict
from troposphere import Ref, GetAtt, Template, GetAZs
from troposphere.ec2 import *


class VpcTemplate:
    """
    Template class which creates a highly opinionated VPC structure.
    """
    STACK_NAME_SUFFIX = 'VpcStack'

    def __init__(self, prefix: str, region: str) -> None:
        """
        Constructor.

        :param prefix: Prefix for the resource names.
        """
        self.__region = region
        self.__prefix = prefix

        self.__vpc = VPC(
            prefix + 'Vpc',
            CidrBlock='10.0.0.0/16',
            InstanceTenancy='default',
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
            Tags=Tags(
                Name=prefix + self.STACK_NAME_SUFFIX
            )
        )

        # Subnets that have full internet access.
        self.__public_subnets = {}
        self.__public_table_associations = []
        self.__public_table = None
        self.__public_route = None

        # Subnets that do not have an external access to internet, only within VPC.
        self.__isolated_subnets = {}
        self.__isolated_table_associations = []
        self.__isolated_table = None

        # Subnets that have access to internet only through NAT gateway.
        self.__private_subnets = {}
        self.__private_table_associations = []
        self.__private_table = None
        self.__private_route = None

        self.__nat_gateway = None
        self.__nat_gateway_ip = None
        self.__internet_gateway = None
        self.__internet_gateway_attachment = None

        # Populate subnets.
        self.__initialize()

    @property
    def vpc(self) -> VPC:
        """
        AWS VPC property.

        :return: Returns AWS VPC instance.
        """
        return self.__vpc

    @property
    def public_subnets(self) -> Dict[str, Subnet]:
        return self.__public_subnets

    @property
    def private_subnets(self) -> Dict[str, Subnet]:
        return self.__private_subnets

    @property
    def isolated_subnets(self) -> Dict[str, Subnet]:
        return self.__isolated_subnets

    @property
    def first_public(self) -> Subnet:
        return list(self.public_subnets.values())[0]

    @property
    def first_private(self) -> Subnet:
        return list(self.private_subnets.values())[0]

    @property
    def first_isolated(self) -> Subnet:
        return list(self.isolated_subnets.values())[0]

    def get_template(self) -> Template:
        template = Template()

        template.add_resource(self.__vpc)

        template.add_resource(self.__isolated_table)
        template.add_resource(self.__private_table)
        template.add_resource(self.__public_table)

        template.add_resource(self.__private_route)
        template.add_resource(self.__public_route)

        template.add_resource(self.__nat_gateway)
        template.add_resource(self.__nat_gateway_ip)
        template.add_resource(self.__internet_gateway)
        template.add_resource(self.__internet_gateway_attachment)

        public = list(self.public_subnets.values())
        private = list(self.private_subnets.values())
        isolated = list(self.isolated_subnets.values())

        for subnet in public + private + isolated:
            template.add_resource(subnet)

        associations = (
                self.__public_table_associations +
                self.__private_table_associations +
                self.__isolated_table_associations
        )

        for association in associations:
            template.add_resource(association)

        return template

    def __initialize(self):
        """
        Creates private, isolated and public subnets for each availability zone.
        Creates corresponding route tables and routes.
        """

        """
        Tables.
        """

        self.__public_table = RouteTable(
            self.__prefix + 'PublicRouteTable',
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=self.__prefix + 'PublicRouteTable'
            ),
        )

        self.__private_table = RouteTable(
            self.__prefix + 'PrivateRouteTable',
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=self.__prefix + 'PrivateRouteTable'
            ),
        )

        self.__isolated_table = RouteTable(
            self.__prefix + 'IsolatedRouteTable',
            VpcId=Ref(self.vpc),
            Tags=Tags(
                Name=self.__prefix + 'IsolatedRouteTable'
            ),
        )

        """
        Subnets.
        """

        az_map = {
            0: self.__region + 'a',
            1: self.__region + 'b',
            2: self.__region + 'c'
        }

        total_index = 0
        for index in range(3):
            az = az_map[index]

            total_index += 1
            self.__public_subnets[az] = self.__create('PublicSubnet', az, total_index)

            total_index += 1
            self.__private_subnets[az] = self.__create('PrivateSubnet', az, total_index)

            total_index += 1
            self.__isolated_subnets[az] = self.__create('IsolatedSubnet', az, total_index)

        """
        Gateways
        """

        self.__nat_gateway_ip = EIP(
            self.__prefix + 'NatGatewayElasticIp',
            Domain='vpc',
        )

        self.__nat_gateway = NatGateway(
            self.__prefix + 'NatGateway',
            AllocationId=GetAtt(self.__nat_gateway_ip, 'AllocationId'),
            SubnetId=Ref(self.first_public),
            Tags=Tags(
                Name=self.__prefix + 'NatGateway'
            )
        )

        self.__internet_gateway = InternetGateway(
            self.__prefix + 'InternetGateway',
            Tags=Tags(
                Name=self.__prefix + 'InternetGateway'
            ),
        )

        self.__internet_gateway_attachment = VPCGatewayAttachment(
            self.__prefix + 'InternetGatewayAttachment',
            InternetGatewayId=Ref(self.__internet_gateway),
            VpcId=Ref(self.vpc),
        )

        """
        Routes.
        """

        self.__public_route = Route(
            self.__prefix + 'RouteToInternetGateway',
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref(self.__internet_gateway),
            RouteTableId=Ref(self.__public_table),
            DependsOn=self.__internet_gateway_attachment.title
        )

        self.__private_route = Route(
            self.__prefix + 'RouteToNatGateway',
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref(self.__nat_gateway),
            RouteTableId=Ref(self.__private_table),
        )

        """
        Associations.
        """

        for index, subnet in enumerate(self.public_subnets.values()):
            association = SubnetRouteTableAssociation(
                self.__prefix + f'PublicSubnetAssociation{index + 1}',
                RouteTableId=Ref(self.__public_table),
                SubnetId=Ref(subnet)
            )

            self.__public_table_associations.append(association)

        for index, subnet in enumerate(self.isolated_subnets.values()):
            association = SubnetRouteTableAssociation(
                self.__prefix + f'IsolatedSubnetAssociation{index + 1}',
                RouteTableId=Ref(self.__isolated_table),
                SubnetId=Ref(subnet)
            )

            self.__isolated_table_associations.append(association)

        for index, subnet in enumerate(self.private_subnets.values()):
            association = SubnetRouteTableAssociation(
                self.__prefix + f'PrivateSubnetAssociation{index + 1}',
                RouteTableId=Ref(self.__private_table),
                SubnetId=Ref(subnet)
            )

            self.__private_table_associations.append(association)

    def __create(self, name: str, availability_zone: str, subnet_index: int) -> Subnet:
        az_letter = availability_zone[-1].upper()

        return Subnet(
            az_letter + name,
            AvailabilityZone=availability_zone,
            CidrBlock='10.0.{}.0/22'.format(subnet_index * 16),
            MapPublicIpOnLaunch=False,
            Tags=Tags(
                Name=az_letter + name
            ),
            VpcId=Ref(self.vpc)
        )
