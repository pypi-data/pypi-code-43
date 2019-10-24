import threading
from abc import ABCMeta
from logging import Logger
from typing import Optional

from retrying import retry

from sidecar.aws_error_helper import AwsErrorHelper
from sidecar.aws_session import AwsSession
from sidecar.azure_clp.azure_clients import AzureClientsManager
from sidecar.const import Const
from sidecar.model.objects import AzureSidecarConfiguration
from sidecar.services.exceptions import NotReadyYetError
from sidecar.utils import Utils


class SandboxMetadataFetcher(metaclass=ABCMeta):
    def get_value(self) -> str:
        raise NotImplementedError()


class SandboxPublicAddressFetcher(SandboxMetadataFetcher):
    ATTEMPT_TIMEOUT_MINUTES = 30
    ATTEMPT_INTERVAL_SECONDS = 10

    def __init__(self, logger: Logger, sandbox_id: str):
        self._sandbox_id = sandbox_id
        self._logger = logger
        self._value = None
        self._thread = None
        self._lock = threading.RLock()

    def get_value(self) -> str:
        with self._lock:
            if not self._value and not self._thread:
                result = self._one_time_safe_fetch()
                if result:
                    self._value = result
                else:
                    self._thread = threading.Thread(target=self._fetching_loop, daemon=True)
                    self._thread.start()
            if self._value:
                return self._value
            raise NotReadyYetError()

    def _fetching_loop(self):
        self._logger.info(f'Staring trying to get sandbox public address')
        result = Utils.retry_on_exception(
            func=lambda: self._get_sandbox_public_ip(),
            interval_in_sec=self.ATTEMPT_INTERVAL_SECONDS,
            timeout_in_sec=self.ATTEMPT_TIMEOUT_MINUTES * 60,
            logger=self._logger,
            logger_msg='getting sandbox public address',
            log_every_n_attempts=6 * 2)  # 12 attempts = ~2min
        with self._lock:
            self._value = result
        self._logger.info(f'Sandbox public address is "{result}"')

    def _one_time_safe_fetch(self) -> Optional[str]:
        try:
            return self._get_sandbox_public_ip()
        except:
            return None

    def _get_sandbox_public_ip(self) -> str:
        raise NotImplementedError()


class AwsSandboxPublicAddressFetcher(SandboxPublicAddressFetcher):
    def __init__(self, logger: Logger, sandbox_id: str, aws_session: AwsSession):
        super().__init__(logger=logger, sandbox_id=sandbox_id)
        self._session = aws_session

    # Exponential Backoff starts from 1 sec to 2 min, until 2 min, in case of throttling
    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=1000 * 60 * 2,
           stop_max_delay=1000 * 60 * 2,
           retry_on_exception=AwsErrorHelper.is_throttling_error)
    def _get_sandbox_public_ip(self) -> str:
        # Get ALB stack name
        stack_name = self._session.production_infra_stack_name or self._session.sandbox_stack_name

        # Get ALB arn
        response = self._session.get_cf_client().describe_stack_resource(StackName=stack_name,
                                                                         LogicalResourceId=Const.MAIN_ALB)
        alb_arn = response['StackResourceDetail']['PhysicalResourceId']

        # Get ALB dns
        response = self._session.get_elb_v2_client().describe_load_balancers(LoadBalancerArns=[alb_arn])
        return response['LoadBalancers'][0]['DNSName']


class AzureSandboxPublicAddressFetcher(SandboxPublicAddressFetcher):
    def __init__(self, logger: Logger, sandbox_id: str, clients_manager: AzureClientsManager,
                 config: AzureSidecarConfiguration):
        super().__init__(logger=logger, sandbox_id=sandbox_id)
        self.config = config
        self.clients_manager = clients_manager

    def _get_sandbox_public_ip(self) -> str:
        # Get AG resource group name
        rg_name = self.config.production_id or self.config.sandbox_id

        # Get AG
        ip = self.clients_manager.network_client.public_ip_addresses.get(resource_group_name=rg_name,
                                                                         public_ip_address_name=Const.AG_PUBLIC_IP)
        if not ip.ip_address:
            raise Exception('ApplicationGateway\'s PublicIpAddress resource does not contain the ip yet')

        return ip.ip_address


class K8sSandboxPublicAddressFetcher(SandboxMetadataFetcher):
    def get_value(self) -> str:
        return ''
