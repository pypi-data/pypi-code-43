from multiprocessing import Process
from typing import List
from aws_lambda.deployment.deployment_package import DeploymentPackage
from aws_cf_custom_resources.abstract_custom_service import AbstractCustomService
from aws_cf_custom_resources.global_config_manager import GlobalConfigManager


class CustomResourcesBuilder:
    def __init__(self, region: str, profile: str):
        self.region = region
        self.profile = profile

    def build(self, custom_resource_services: List[AbstractCustomService], upload: bool = True):
        process_pool = []

        for resource in custom_resource_services:
            p = Process(target=self.__build_single, args=(resource, upload))
            p.start()

            process_pool.append(p)

        for process in process_pool:
            process.join(600 if upload else 500)

    def __build_single(self, resource: AbstractCustomService, upload: bool = True):
        DeploymentPackage(
            environment='none',
            project_src_path=resource.src,
            lambda_name=resource.lambda_name,
            s3_upload_bucket=GlobalConfigManager.get_params().custom_resources_bucket,
            s3_bucket_region=self.region,
            aws_profile=self.profile,
            refresh_lambda=upload
        ).deploy()
