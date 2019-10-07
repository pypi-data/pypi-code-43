import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudformation
import aws_cdk.aws_cloudfront
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_s3_assets
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-s3-deployment", "1.12.0", __name__, "aws-s3-deployment@1.12.0.jsii.tgz")
class BucketDeployment(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3-deployment.BucketDeployment"):
    """
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, destination_bucket: aws_cdk.aws_s3.IBucket, sources: typing.List["ISource"], destination_key_prefix: typing.Optional[str]=None, distribution: typing.Optional[aws_cdk.aws_cloudfront.IDistribution]=None, distribution_paths: typing.Optional[typing.List[str]]=None, memory_limit: typing.Optional[jsii.Number]=None, retain_on_delete: typing.Optional[bool]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param destination_bucket: The S3 bucket to sync the contents of the zip file to.
        :param sources: The sources from which to deploy the contents of this bucket.
        :param destination_key_prefix: Key prefix in the destination bucket. Default: "/" (unzip to root of the destination bucket)
        :param distribution: The CloudFront distribution using the destination bucket as an origin. Files in the distribution's edge caches will be invalidated after files are uploaded to the destination bucket. Default: - No invalidation occurs
        :param distribution_paths: The file paths to invalidate in the CloudFront distribution. Default: - All files under the destination bucket key prefix will be invalidated.
        :param memory_limit: The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket. If you are deploying large files, you will need to increase this number accordingly. Default: 128
        :param retain_on_delete: If this is set to "false", the destination files will be deleted when the resource is deleted or the destination is updated. NOTICE: if this is set to "false" and destination bucket/prefix is updated, all files in the previous destination will first be deleted and then uploaded to the new destination location. This could have availablity implications on your users. Default: true - when resource is deleted/updated, files are retained

        stability
        :stability: experimental
        """
        props = BucketDeploymentProps(destination_bucket=destination_bucket, sources=sources, destination_key_prefix=destination_key_prefix, distribution=distribution, distribution_paths=distribution_paths, memory_limit=memory_limit, retain_on_delete=retain_on_delete)

        jsii.create(BucketDeployment, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-s3-deployment.BucketDeploymentProps", jsii_struct_bases=[], name_mapping={'destination_bucket': 'destinationBucket', 'sources': 'sources', 'destination_key_prefix': 'destinationKeyPrefix', 'distribution': 'distribution', 'distribution_paths': 'distributionPaths', 'memory_limit': 'memoryLimit', 'retain_on_delete': 'retainOnDelete'})
class BucketDeploymentProps():
    def __init__(self, *, destination_bucket: aws_cdk.aws_s3.IBucket, sources: typing.List["ISource"], destination_key_prefix: typing.Optional[str]=None, distribution: typing.Optional[aws_cdk.aws_cloudfront.IDistribution]=None, distribution_paths: typing.Optional[typing.List[str]]=None, memory_limit: typing.Optional[jsii.Number]=None, retain_on_delete: typing.Optional[bool]=None):
        """
        :param destination_bucket: The S3 bucket to sync the contents of the zip file to.
        :param sources: The sources from which to deploy the contents of this bucket.
        :param destination_key_prefix: Key prefix in the destination bucket. Default: "/" (unzip to root of the destination bucket)
        :param distribution: The CloudFront distribution using the destination bucket as an origin. Files in the distribution's edge caches will be invalidated after files are uploaded to the destination bucket. Default: - No invalidation occurs
        :param distribution_paths: The file paths to invalidate in the CloudFront distribution. Default: - All files under the destination bucket key prefix will be invalidated.
        :param memory_limit: The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket. If you are deploying large files, you will need to increase this number accordingly. Default: 128
        :param retain_on_delete: If this is set to "false", the destination files will be deleted when the resource is deleted or the destination is updated. NOTICE: if this is set to "false" and destination bucket/prefix is updated, all files in the previous destination will first be deleted and then uploaded to the new destination location. This could have availablity implications on your users. Default: true - when resource is deleted/updated, files are retained

        stability
        :stability: experimental
        """
        self._values = {
            'destination_bucket': destination_bucket,
            'sources': sources,
        }
        if destination_key_prefix is not None: self._values["destination_key_prefix"] = destination_key_prefix
        if distribution is not None: self._values["distribution"] = distribution
        if distribution_paths is not None: self._values["distribution_paths"] = distribution_paths
        if memory_limit is not None: self._values["memory_limit"] = memory_limit
        if retain_on_delete is not None: self._values["retain_on_delete"] = retain_on_delete

    @property
    def destination_bucket(self) -> aws_cdk.aws_s3.IBucket:
        """The S3 bucket to sync the contents of the zip file to.

        stability
        :stability: experimental
        """
        return self._values.get('destination_bucket')

    @property
    def sources(self) -> typing.List["ISource"]:
        """The sources from which to deploy the contents of this bucket.

        stability
        :stability: experimental
        """
        return self._values.get('sources')

    @property
    def destination_key_prefix(self) -> typing.Optional[str]:
        """Key prefix in the destination bucket.

        default
        :default: "/" (unzip to root of the destination bucket)

        stability
        :stability: experimental
        """
        return self._values.get('destination_key_prefix')

    @property
    def distribution(self) -> typing.Optional[aws_cdk.aws_cloudfront.IDistribution]:
        """The CloudFront distribution using the destination bucket as an origin. Files in the distribution's edge caches will be invalidated after files are uploaded to the destination bucket.

        default
        :default: - No invalidation occurs

        stability
        :stability: experimental
        """
        return self._values.get('distribution')

    @property
    def distribution_paths(self) -> typing.Optional[typing.List[str]]:
        """The file paths to invalidate in the CloudFront distribution.

        default
        :default: - All files under the destination bucket key prefix will be invalidated.

        stability
        :stability: experimental
        """
        return self._values.get('distribution_paths')

    @property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        """The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket.

        If you are deploying large files, you will need to increase this number
        accordingly.

        default
        :default: 128

        stability
        :stability: experimental
        """
        return self._values.get('memory_limit')

    @property
    def retain_on_delete(self) -> typing.Optional[bool]:
        """If this is set to "false", the destination files will be deleted when the resource is deleted or the destination is updated.

        NOTICE: if this is set to "false" and destination bucket/prefix is updated,
        all files in the previous destination will first be deleted and then
        uploaded to the new destination location. This could have availablity
        implications on your users.

        default
        :default: true - when resource is deleted/updated, files are retained

        stability
        :stability: experimental
        """
        return self._values.get('retain_on_delete')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'BucketDeploymentProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.interface(jsii_type="@aws-cdk/aws-s3-deployment.ISource")
class ISource(jsii.compat.Protocol):
    """Represents a source for bucket deployments.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISourceProxy

    @jsii.member(jsii_name="bind")
    def bind(self, context: aws_cdk.core.Construct) -> "SourceConfig":
        """Binds the source to a bucket deployment.

        :param context: The construct tree context.

        stability
        :stability: experimental
        """
        ...


class _ISourceProxy():
    """Represents a source for bucket deployments.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-s3-deployment.ISource"
    @jsii.member(jsii_name="bind")
    def bind(self, context: aws_cdk.core.Construct) -> "SourceConfig":
        """Binds the source to a bucket deployment.

        :param context: The construct tree context.

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "bind", [context])


class Source(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-s3-deployment.Source"):
    """Specifies bucket deployment source.

    Usage::

        Source.bucket(bucket, key)
        Source.asset('/local/path/to/directory')
        Source.asset('/local/path/to/a/file.zip')

    stability
    :stability: experimental
    """
    @jsii.member(jsii_name="asset")
    @classmethod
    def asset(cls, path: str) -> "ISource":
        """Uses a local asset as the deployment source.

        :param path: The path to a local .zip file or a directory.

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "asset", [path])

    @jsii.member(jsii_name="bucket")
    @classmethod
    def bucket(cls, bucket: aws_cdk.aws_s3.IBucket, zip_object_key: str) -> "ISource":
        """Uses a .zip file stored in an S3 bucket as the source for the destination bucket contents.

        :param bucket: The S3 Bucket.
        :param zip_object_key: The S3 object key of the zip file with contents.

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "bucket", [bucket, zip_object_key])


@jsii.data_type(jsii_type="@aws-cdk/aws-s3-deployment.SourceConfig", jsii_struct_bases=[], name_mapping={'bucket': 'bucket', 'zip_object_key': 'zipObjectKey'})
class SourceConfig():
    def __init__(self, *, bucket: aws_cdk.aws_s3.IBucket, zip_object_key: str):
        """
        :param bucket: The source bucket to deploy from.
        :param zip_object_key: An S3 object key in the source bucket that points to a zip file.

        stability
        :stability: experimental
        """
        self._values = {
            'bucket': bucket,
            'zip_object_key': zip_object_key,
        }

    @property
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        """The source bucket to deploy from.

        stability
        :stability: experimental
        """
        return self._values.get('bucket')

    @property
    def zip_object_key(self) -> str:
        """An S3 object key in the source bucket that points to a zip file.

        stability
        :stability: experimental
        """
        return self._values.get('zip_object_key')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'SourceConfig(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["BucketDeployment", "BucketDeploymentProps", "ISource", "Source", "SourceConfig", "__jsii_assembly__"]

publication.publish()
