# -*- coding: utf-8 -*-

from troposphere_mate.core.canned import MultiEnvBasicConfig, Constant, Derivable


class Config(MultiEnvBasicConfig):
    PROJECT_NAME = Constant()
    PROJECT_NAME_SLUG = Derivable()

    @PROJECT_NAME_SLUG.getter
    def get_project_name_slug(self):
        return self.PROJECT_NAME.get_value().replace("_", "-")

    STAGE = Constant()  # example dev / test / prod

    ENVIRONMENT_NAME = Derivable()

    ENV_TAG = Derivable()

    @ENV_TAG.getter
    def get_ENV_TAG(self):
        return self.STAGE.get_value()

    @ENVIRONMENT_NAME.getter
    def get_ENVIRONMENT_NAME(self):
        return "{}-{}".format(self.PROJECT_NAME_SLUG.get_value(self), self.STAGE.get_value())

    AWS_PROFILE = Constant()
    AWS_ACCOUNT_ALIAS = Constant()

    S3_BUCKET_FOR_CF = Constant()

    VPC_CIDR_ID = Constant()  # an Integer between 0 - 255

    VPC_CIDR = Derivable()

    @VPC_CIDR.getter
    def get_VPC_CIDR(self):
        return "10.{}.0.0/16".format(self.VPC_CIDR_ID.get_value())

    N_PUBLIC_SUBNET = Constant()
    N_PRIVATE_SUBNET = Constant()

    def get_nth_public_subnet_cidr(self, nth):
        return "10.{}.{}.0/24".format(
            self.VPC_CIDR_ID.get_value(),
            (nth - 1) * 2,
        )

    def get_nth_private_subnet_cidr(self, nth):
        return "10.{}.{}.0/24".format(
            self.VPC_CIDR_ID.get_value(),
            (nth - 1) * 2 + 1,
        )

    PUBLIC_SUBNET_CIDR_LIST = Derivable()

    @PUBLIC_SUBNET_CIDR_LIST.getter
    def get_PUBLIC_SUBNET_CIDR_LIST(self):
        return [
            self.get_nth_public_subnet_cidr(nth)
            for nth in range(1, 1 + self.N_PUBLIC_SUBNET.get_value())
        ]

    PRIVATE_SUBNET_CIDR_LIST = Derivable()

    @PRIVATE_SUBNET_CIDR_LIST.getter
    def get_PUBLIC_SUBNET_CIDR_LIST(self):
        return [
            self.get_nth_private_subnet_cidr(nth)
            for nth in range(1, 1 + self.N_PUBLIC_SUBNET.get_value())
        ]

    USE_NAT_GW_PER_PRIVATE_SUBNET_FLAG = Constant()

    @USE_NAT_GW_PER_PRIVATE_SUBNET_FLAG.validator
    def check_use_nat_gw_per_private_subnet_flag(self, value):
        if value is True:
            if self.N_PUBLIC_SUBNET.get_value() < self.N_PRIVATE_SUBNET.get_value():
                raise ValueError("If you want to use 1 independent Nat GW "
                                 "Per Private Subnet, then the number of "
                                 "public subnet has to be greater than "
                                 "private subnet.")

    NUMBER_OF_NAT_GW = Derivable()

    @NUMBER_OF_NAT_GW.getter
    def get_number_of_nat_gw(self):
        if self.USE_NAT_GW_PER_PRIVATE_SUBNET_FLAG.get_value():
            return self.N_PUBLIC_SUBNET.get_value()
        else:
            return 1

    TIER_LIST_TO_DEPLOY = Constant()
