# -*- coding: utf-8 -*-

try:
    from typing import List
except:
    pass

from troposphere_mate import ec2
from troposphere_mate import Select, GetAZs, Ref, Tags, Template, Output
from troposphere_mate.orch_example.web_app.config import Config


class AZPropertyValues:
    the_01_th = Select(0, GetAZs())
    the_02_th = Select(1, GetAZs())
    the_03_th = Select(2, GetAZs())
    the_04_th = Select(3, GetAZs())
    the_05_th = Select(4, GetAZs())
    the_06_th = Select(5, GetAZs())
    the_07_th = Select(6, GetAZs())
    the_08_th = Select(7, GetAZs())
    the_09_th = Select(8, GetAZs())
    the_10_th = Select(9, GetAZs())

    @classmethod
    def get_nth_az(cls, nth):
        return Select(nth - 1, GetAZs())


class VPCTier(Config):
    rel_path = "01-vpc.json"

    vpc = None  # type: ec2.VPC
    public_subnet_list = None  # type: List[ec2.Subnet]
    private_subnet_list = None  # type: List[ec2.Subnet]
    subnet_list = None  # type: List[ec2.Subnet]
    igw = None  # type: ec2.InternetGateway
    eip_list = None  # type: List[ec2.EIP]
    ngw_list = None  # type: List[ec2.NatGateway]
    public_route_table = None  # type: ec2.RouteTable
    sg_for_ssh = None  # type: ec2.SecurityGroup

    def do_create_template(self):
        template = Template()
        self.template = template

        vpc = ec2.VPC(
            "VPC",
            template=template,
            CidrBlock=self.VPC_CIDR.get_value(),
        )
        self.vpc = vpc

        public_subnet_list = list()
        for ind, cidr in enumerate(self.PUBLIC_SUBNET_CIDR_LIST.get_value()):
            subnet = ec2.Subnet(
                "PublicSubnet{}".format(ind + 1),
                template=template,
                CidrBlock=cidr,
                VpcId=Ref(vpc),
                AvailabilityZone=AZPropertyValues.get_nth_az(ind + 1),
                MapPublicIpOnLaunch=True,
                Tags=Tags(Name="{}/ngw/public{}".format(
                    self.ENVIRONMENT_NAME.get_value(),
                    ind + 1,
                )),
                DependsOn=[vpc, ],
            )
            public_subnet_list.append(subnet)
        self.public_subnet_list = public_subnet_list

        private_subnet_list = list()
        for ind, cidr in enumerate(self.PRIVATE_SUBNET_CIDR_LIST.get_value()):
            subnet = ec2.Subnet(
                "PrivateSubnet{}".format(ind + 1),
                template=template,
                CidrBlock=cidr,
                VpcId=Ref(vpc),
                AvailabilityZone=AZPropertyValues.get_nth_az(ind + 1),
                MapPublicIpOnLaunch=True,
                Tags=Tags(Name="{}/ngw/priavte{}".format(
                    self.ENVIRONMENT_NAME.get_value(),
                    ind + 1,
                )),
                DependsOn=[vpc, ],
            )
            private_subnet_list.append(subnet)
        self.private_subnet_list = private_subnet_list

        subnet_list = public_subnet_list + private_subnet_list
        self.subnet_list = subnet_list

        # igw for public subnet
        igw = ec2.InternetGateway(
            "IGW",
            template=template,
        )
        igw_attach_vpc = ec2.VPCGatewayAttachment(
            "IGWAttachVPC",
            template=template,
            VpcId=Ref(vpc),
        )
        self.igw = igw

        # eip + ngw is on public subnet but for private subnet traffic out
        eip_list = list()
        ngw_list = list()
        for ind in range(1, 1 + self.NUMBER_OF_NAT_GW.get_value()):
            eip = ec2.EIP(
                "EIP{}".format(ind),
                template=template,
                Domain="vpc",
            )
            eip_list.append(eip)

            ngw = ec2.NatGateway(
                "NGW{}".format(ind),
                template=template,
                AllocationId=Ref(eip),
                SubnetId=Ref(public_subnet_list[ind - 1]),
                Tags=Tags(Name="{}/ngw/public{}".format(
                    self.ENVIRONMENT_NAME.get_value(),
                    ind,
                ))
            )
            ngw_list.append(ngw)
        self.eip_list = eip_list
        self.ngw_list = ngw_list

        # public route
        public_route_table = ec2.RouteTable(
            "PublicRouteTable",
            template=template,
            VpcId=Ref(vpc),
            Tags=Tags(Name="{}/public-routes".format(
                self.ENVIRONMENT_NAME.get_value(),
            ))
        )
        public_route_default = ec2.Route(
            "PublicRouteDefault",
            template=template,
            RouteTableId=Ref(public_route_table),
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=Ref(igw),
            DependsOn=[public_route_table, igw],
        )

        for ind, subnet in enumerate(public_subnet_list):
            route_table_association = ec2.SubnetRouteTableAssociation(
                "PublicSubnet{}RouteTableAssociation".format(ind + 1),
                RouteTableId=Ref(public_route_table),
                SubnetId=Ref(subnet),
                DependsOn=[public_route_table, subnet],
            )

        # private route

        if self.USE_NAT_GW_PER_PRIVATE_SUBNET_FLAG.get_value() is True:
            for ind, subnet in enumerate(private_subnet_list):
                private_route_table = ec2.RouteTable(
                    "PrivateRouteTable{}".format(ind + 1),
                    template=template,
                    VpcId=Ref(vpc),
                    Tags=Tags(Name="{}/private-routes{}".format(
                        self.ENVIRONMENT_NAME.get_value(),
                        ind + 1,
                    ))
                )
                private_route_default = ec2.Route(
                    "PrivateRoute{}Default".format(ind + 1),
                    template=template,
                    RouteTableId=Ref(private_route_table),
                    DestinationCidrBlock="0.0.0.0/0",
                    GatewayId=Ref(ngw_list[ind]),
                    DependsOn=[private_route_table, ngw_list[ind]],
                )
                route_table_association = ec2.SubnetRouteTableAssociation(
                    "PrivateSubnet{}RouteTableAssociation".format(ind + 1),
                    RouteTableId=Ref(private_route_table),
                    SubnetId=Ref(subnet),
                    DependsOn=[private_route_table, subnet],
                )
        else:
            private_route_table = ec2.RouteTable(
                "PrivateRouteTable",
                template=template,
                VpcId=Ref(vpc),
                Tags=Tags(Name="{}/private-routes".format(
                    self.ENVIRONMENT_NAME.get_value(),
                ))
            )
            private_route_default = ec2.Route(
                "PrivateRouteDefault",
                template=template,
                RouteTableId=Ref(private_route_table),
                DestinationCidrBlock="0.0.0.0/0",
                GatewayId=Ref(ngw_list[0]),
                DependsOn=[private_route_table, ngw_list[0]],
            )
            for ind, subnet in enumerate(private_subnet_list):
                route_table_association = ec2.SubnetRouteTableAssociation(
                    "PrivateSubnet{}RouteTableAssociation".format(ind + 1),
                    RouteTableId=Ref(private_route_table),
                    SubnetId=Ref(subnet),
                    DependsOn=[private_route_table, subnet],
                )

        group_name = "{}/sg/allow-ssh-from-anywhere".format(
            self.ENVIRONMENT_NAME.get_value())
        sg_for_ssh = ec2.SecurityGroup(
            "SGForSSH",
            template=template,
            GroupDescription="Allow SSH In",
            GroupName=group_name,
            VpcId=Ref(vpc),
            SecurityGroupIngress=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "CidrIp": "0.0.0.0/0"
                }
            ],
            Tags=Tags(Name=group_name),
        )
        self.sg_for_ssh = sg_for_ssh

        outputs = [
            Output("VPC", Description="VPC ID", Value=Ref(vpc)),
            Output(sg_for_ssh.title, Description="Security Group ID",
                   Value=Ref(sg_for_ssh))
        ]
        for subnet in subnet_list:
            output = Output(subnet.title, Description="{} ID".format(
                subnet.title), Value=Ref(subnet))
            outputs.append(output)

        common_tags = dict(
            Name=self.ENVIRONMENT_NAME.get_value(),
            Project=self.PROJECT_NAME_SLUG.get_value(),
            Stage=self.STAGE.get_value(),
            EnvName=self.ENVIRONMENT_NAME.get_value(),
        )
        template.update_tags(common_tags, overwrite=False)
        return template

    def get_nth_public_subnet(self, nth):
        return self.public_subnet_list[nth-1]

    def get_nth_private_subnet(self, nth):
        return self.private_subnet_list[nth-1]


if __name__ == "__main__":
    from superjson import json
    can = VPCTier(
        PROJECT_NAME="myprojet",
        STAGE="dev",
        VPC_CIDR_ID=192,
        N_PUBLIC_SUBNET=3,
        N_PRIVATE_SUBNET=3,
        USE_NAT_GW_PER_PRIVATE_SUBNET_FLAG=False,
    )
    can.create_template()
    can.template.pprint()
