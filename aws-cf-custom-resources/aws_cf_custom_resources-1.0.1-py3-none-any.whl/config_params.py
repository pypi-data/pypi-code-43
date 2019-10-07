class ConfigurationParameters:
    __CF_CUSTOM_BUILDS_BUCKET = 'aws.infrastructure.sdk.cf.custom.resources.{}'

    def __init__(
            self,
            custom_resources_bucket_suffix: str
    ) -> None:
        assert custom_resources_bucket_suffix
        self.__custom_resources_bucket_suffix: str = custom_resources_bucket_suffix

    @property
    def custom_resources_bucket(self) -> str:
        return self.__CF_CUSTOM_BUILDS_BUCKET.format(self.__custom_resources_bucket_suffix)
