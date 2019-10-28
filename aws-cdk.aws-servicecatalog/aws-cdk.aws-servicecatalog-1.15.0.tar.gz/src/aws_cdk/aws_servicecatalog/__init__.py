import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-servicecatalog", "1.15.0", __name__, "aws-servicecatalog@1.15.0.jsii.tgz")
class CfnAcceptedPortfolioShare(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnAcceptedPortfolioShare"):
    """A CloudFormation ``AWS::ServiceCatalog::AcceptedPortfolioShare``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-acceptedportfolioshare.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::AcceptedPortfolioShare
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, portfolio_id: str, accept_language: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::AcceptedPortfolioShare``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param portfolio_id: ``AWS::ServiceCatalog::AcceptedPortfolioShare.PortfolioId``.
        :param accept_language: ``AWS::ServiceCatalog::AcceptedPortfolioShare.AcceptLanguage``.
        """
        props = CfnAcceptedPortfolioShareProps(portfolio_id=portfolio_id, accept_language=accept_language)

        jsii.create(CfnAcceptedPortfolioShare, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::AcceptedPortfolioShare.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-acceptedportfolioshare.html#cfn-servicecatalog-acceptedportfolioshare-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::AcceptedPortfolioShare.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-acceptedportfolioshare.html#cfn-servicecatalog-acceptedportfolioshare-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnAcceptedPortfolioShareProps", jsii_struct_bases=[], name_mapping={'portfolio_id': 'portfolioId', 'accept_language': 'acceptLanguage'})
class CfnAcceptedPortfolioShareProps():
    def __init__(self, *, portfolio_id: str, accept_language: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::AcceptedPortfolioShare``.

        :param portfolio_id: ``AWS::ServiceCatalog::AcceptedPortfolioShare.PortfolioId``.
        :param accept_language: ``AWS::ServiceCatalog::AcceptedPortfolioShare.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-acceptedportfolioshare.html
        """
        self._values = {
            'portfolio_id': portfolio_id,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::AcceptedPortfolioShare.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-acceptedportfolioshare.html#cfn-servicecatalog-acceptedportfolioshare-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::AcceptedPortfolioShare.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-acceptedportfolioshare.html#cfn-servicecatalog-acceptedportfolioshare-acceptlanguage
        """
        return self._values.get('accept_language')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAcceptedPortfolioShareProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnCloudFormationProduct(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProduct"):
    """A CloudFormation ``AWS::ServiceCatalog::CloudFormationProduct``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::CloudFormationProduct
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, owner: str, provisioning_artifact_parameters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ProvisioningArtifactPropertiesProperty", aws_cdk.core.IResolvable]]], accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None, distributor: typing.Optional[str]=None, support_description: typing.Optional[str]=None, support_email: typing.Optional[str]=None, support_url: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::CloudFormationProduct``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::ServiceCatalog::CloudFormationProduct.Name``.
        :param owner: ``AWS::ServiceCatalog::CloudFormationProduct.Owner``.
        :param provisioning_artifact_parameters: ``AWS::ServiceCatalog::CloudFormationProduct.ProvisioningArtifactParameters``.
        :param accept_language: ``AWS::ServiceCatalog::CloudFormationProduct.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::CloudFormationProduct.Description``.
        :param distributor: ``AWS::ServiceCatalog::CloudFormationProduct.Distributor``.
        :param support_description: ``AWS::ServiceCatalog::CloudFormationProduct.SupportDescription``.
        :param support_email: ``AWS::ServiceCatalog::CloudFormationProduct.SupportEmail``.
        :param support_url: ``AWS::ServiceCatalog::CloudFormationProduct.SupportUrl``.
        :param tags: ``AWS::ServiceCatalog::CloudFormationProduct.Tags``.
        """
        props = CfnCloudFormationProductProps(name=name, owner=owner, provisioning_artifact_parameters=provisioning_artifact_parameters, accept_language=accept_language, description=description, distributor=distributor, support_description=support_description, support_email=support_email, support_url=support_url, tags=tags)

        jsii.create(CfnCloudFormationProduct, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrProductName")
    def attr_product_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ProductName
        """
        return jsii.get(self, "attrProductName")

    @property
    @jsii.member(jsii_name="attrProvisioningArtifactIds")
    def attr_provisioning_artifact_ids(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ProvisioningArtifactIds
        """
        return jsii.get(self, "attrProvisioningArtifactIds")

    @property
    @jsii.member(jsii_name="attrProvisioningArtifactNames")
    def attr_provisioning_artifact_names(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ProvisioningArtifactNames
        """
        return jsii.get(self, "attrProvisioningArtifactNames")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::ServiceCatalog::CloudFormationProduct.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::ServiceCatalog::CloudFormationProduct.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="owner")
    def owner(self) -> str:
        """``AWS::ServiceCatalog::CloudFormationProduct.Owner``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-owner
        """
        return jsii.get(self, "owner")

    @owner.setter
    def owner(self, value: str):
        return jsii.set(self, "owner", value)

    @property
    @jsii.member(jsii_name="provisioningArtifactParameters")
    def provisioning_artifact_parameters(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ProvisioningArtifactPropertiesProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::ServiceCatalog::CloudFormationProduct.ProvisioningArtifactParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-provisioningartifactparameters
        """
        return jsii.get(self, "provisioningArtifactParameters")

    @provisioning_artifact_parameters.setter
    def provisioning_artifact_parameters(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ProvisioningArtifactPropertiesProperty", aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "provisioningArtifactParameters", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="distributor")
    def distributor(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.Distributor``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-distributor
        """
        return jsii.get(self, "distributor")

    @distributor.setter
    def distributor(self, value: typing.Optional[str]):
        return jsii.set(self, "distributor", value)

    @property
    @jsii.member(jsii_name="supportDescription")
    def support_description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.SupportDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-supportdescription
        """
        return jsii.get(self, "supportDescription")

    @support_description.setter
    def support_description(self, value: typing.Optional[str]):
        return jsii.set(self, "supportDescription", value)

    @property
    @jsii.member(jsii_name="supportEmail")
    def support_email(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.SupportEmail``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-supportemail
        """
        return jsii.get(self, "supportEmail")

    @support_email.setter
    def support_email(self, value: typing.Optional[str]):
        return jsii.set(self, "supportEmail", value)

    @property
    @jsii.member(jsii_name="supportUrl")
    def support_url(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.SupportUrl``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-supporturl
        """
        return jsii.get(self, "supportUrl")

    @support_url.setter
    def support_url(self, value: typing.Optional[str]):
        return jsii.set(self, "supportUrl", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty", jsii_struct_bases=[], name_mapping={'info': 'info', 'description': 'description', 'disable_template_validation': 'disableTemplateValidation', 'name': 'name'})
    class ProvisioningArtifactPropertiesProperty():
        def __init__(self, *, info: typing.Any, description: typing.Optional[str]=None, disable_template_validation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, name: typing.Optional[str]=None):
            """
            :param info: ``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.Info``.
            :param description: ``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.Description``.
            :param disable_template_validation: ``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.DisableTemplateValidation``.
            :param name: ``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationproduct-provisioningartifactproperties.html
            """
            self._values = {
                'info': info,
            }
            if description is not None: self._values["description"] = description
            if disable_template_validation is not None: self._values["disable_template_validation"] = disable_template_validation
            if name is not None: self._values["name"] = name

        @property
        def info(self) -> typing.Any:
            """``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.Info``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationproduct-provisioningartifactproperties.html#cfn-servicecatalog-cloudformationproduct-provisioningartifactproperties-info
            """
            return self._values.get('info')

        @property
        def description(self) -> typing.Optional[str]:
            """``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.Description``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationproduct-provisioningartifactproperties.html#cfn-servicecatalog-cloudformationproduct-provisioningartifactproperties-description
            """
            return self._values.get('description')

        @property
        def disable_template_validation(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.DisableTemplateValidation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationproduct-provisioningartifactproperties.html#cfn-servicecatalog-cloudformationproduct-provisioningartifactproperties-disabletemplatevalidation
            """
            return self._values.get('disable_template_validation')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationproduct-provisioningartifactproperties.html#cfn-servicecatalog-cloudformationproduct-provisioningartifactproperties-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProvisioningArtifactPropertiesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProductProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'owner': 'owner', 'provisioning_artifact_parameters': 'provisioningArtifactParameters', 'accept_language': 'acceptLanguage', 'description': 'description', 'distributor': 'distributor', 'support_description': 'supportDescription', 'support_email': 'supportEmail', 'support_url': 'supportUrl', 'tags': 'tags'})
class CfnCloudFormationProductProps():
    def __init__(self, *, name: str, owner: str, provisioning_artifact_parameters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty", aws_cdk.core.IResolvable]]], accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None, distributor: typing.Optional[str]=None, support_description: typing.Optional[str]=None, support_email: typing.Optional[str]=None, support_url: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::ServiceCatalog::CloudFormationProduct``.

        :param name: ``AWS::ServiceCatalog::CloudFormationProduct.Name``.
        :param owner: ``AWS::ServiceCatalog::CloudFormationProduct.Owner``.
        :param provisioning_artifact_parameters: ``AWS::ServiceCatalog::CloudFormationProduct.ProvisioningArtifactParameters``.
        :param accept_language: ``AWS::ServiceCatalog::CloudFormationProduct.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::CloudFormationProduct.Description``.
        :param distributor: ``AWS::ServiceCatalog::CloudFormationProduct.Distributor``.
        :param support_description: ``AWS::ServiceCatalog::CloudFormationProduct.SupportDescription``.
        :param support_email: ``AWS::ServiceCatalog::CloudFormationProduct.SupportEmail``.
        :param support_url: ``AWS::ServiceCatalog::CloudFormationProduct.SupportUrl``.
        :param tags: ``AWS::ServiceCatalog::CloudFormationProduct.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html
        """
        self._values = {
            'name': name,
            'owner': owner,
            'provisioning_artifact_parameters': provisioning_artifact_parameters,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if description is not None: self._values["description"] = description
        if distributor is not None: self._values["distributor"] = distributor
        if support_description is not None: self._values["support_description"] = support_description
        if support_email is not None: self._values["support_email"] = support_email
        if support_url is not None: self._values["support_url"] = support_url
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::ServiceCatalog::CloudFormationProduct.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-name
        """
        return self._values.get('name')

    @property
    def owner(self) -> str:
        """``AWS::ServiceCatalog::CloudFormationProduct.Owner``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-owner
        """
        return self._values.get('owner')

    @property
    def provisioning_artifact_parameters(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnCloudFormationProduct.ProvisioningArtifactPropertiesProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::ServiceCatalog::CloudFormationProduct.ProvisioningArtifactParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-provisioningartifactparameters
        """
        return self._values.get('provisioning_artifact_parameters')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-description
        """
        return self._values.get('description')

    @property
    def distributor(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.Distributor``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-distributor
        """
        return self._values.get('distributor')

    @property
    def support_description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.SupportDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-supportdescription
        """
        return self._values.get('support_description')

    @property
    def support_email(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.SupportEmail``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-supportemail
        """
        return self._values.get('support_email')

    @property
    def support_url(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProduct.SupportUrl``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-supporturl
        """
        return self._values.get('support_url')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::ServiceCatalog::CloudFormationProduct.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationproduct.html#cfn-servicecatalog-cloudformationproduct-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCloudFormationProductProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnCloudFormationProvisionedProduct(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProvisionedProduct"):
    """A CloudFormation ``AWS::ServiceCatalog::CloudFormationProvisionedProduct``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::CloudFormationProvisionedProduct
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, accept_language: typing.Optional[str]=None, notification_arns: typing.Optional[typing.List[str]]=None, path_id: typing.Optional[str]=None, product_id: typing.Optional[str]=None, product_name: typing.Optional[str]=None, provisioned_product_name: typing.Optional[str]=None, provisioning_artifact_id: typing.Optional[str]=None, provisioning_artifact_name: typing.Optional[str]=None, provisioning_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ProvisioningParameterProperty"]]]]]=None, provisioning_preferences: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ProvisioningPreferencesProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::CloudFormationProvisionedProduct``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param accept_language: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.AcceptLanguage``.
        :param notification_arns: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.NotificationArns``.
        :param path_id: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.PathId``.
        :param product_id: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductId``.
        :param product_name: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductName``.
        :param provisioned_product_name: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisionedProductName``.
        :param provisioning_artifact_id: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactId``.
        :param provisioning_artifact_name: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactName``.
        :param provisioning_parameters: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningParameters``.
        :param provisioning_preferences: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningPreferences``.
        :param tags: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.Tags``.
        """
        props = CfnCloudFormationProvisionedProductProps(accept_language=accept_language, notification_arns=notification_arns, path_id=path_id, product_id=product_id, product_name=product_name, provisioned_product_name=provisioned_product_name, provisioning_artifact_id=provisioning_artifact_id, provisioning_artifact_name=provisioning_artifact_name, provisioning_parameters=provisioning_parameters, provisioning_preferences=provisioning_preferences, tags=tags)

        jsii.create(CfnCloudFormationProvisionedProduct, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrCloudformationStackArn")
    def attr_cloudformation_stack_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: CloudformationStackArn
        """
        return jsii.get(self, "attrCloudformationStackArn")

    @property
    @jsii.member(jsii_name="attrRecordId")
    def attr_record_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: RecordId
        """
        return jsii.get(self, "attrRecordId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.NotificationArns``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-notificationarns
        """
        return jsii.get(self, "notificationArns")

    @notification_arns.setter
    def notification_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "notificationArns", value)

    @property
    @jsii.member(jsii_name="pathId")
    def path_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.PathId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-pathid
        """
        return jsii.get(self, "pathId")

    @path_id.setter
    def path_id(self, value: typing.Optional[str]):
        return jsii.set(self, "pathId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: typing.Optional[str]):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="productName")
    def product_name(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-productname
        """
        return jsii.get(self, "productName")

    @product_name.setter
    def product_name(self, value: typing.Optional[str]):
        return jsii.set(self, "productName", value)

    @property
    @jsii.member(jsii_name="provisionedProductName")
    def provisioned_product_name(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisionedProductName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisionedproductname
        """
        return jsii.get(self, "provisionedProductName")

    @provisioned_product_name.setter
    def provisioned_product_name(self, value: typing.Optional[str]):
        return jsii.set(self, "provisionedProductName", value)

    @property
    @jsii.member(jsii_name="provisioningArtifactId")
    def provisioning_artifact_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningartifactid
        """
        return jsii.get(self, "provisioningArtifactId")

    @provisioning_artifact_id.setter
    def provisioning_artifact_id(self, value: typing.Optional[str]):
        return jsii.set(self, "provisioningArtifactId", value)

    @property
    @jsii.member(jsii_name="provisioningArtifactName")
    def provisioning_artifact_name(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningartifactname
        """
        return jsii.get(self, "provisioningArtifactName")

    @provisioning_artifact_name.setter
    def provisioning_artifact_name(self, value: typing.Optional[str]):
        return jsii.set(self, "provisioningArtifactName", value)

    @property
    @jsii.member(jsii_name="provisioningParameters")
    def provisioning_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ProvisioningParameterProperty"]]]]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningparameters
        """
        return jsii.get(self, "provisioningParameters")

    @provisioning_parameters.setter
    def provisioning_parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ProvisioningParameterProperty"]]]]]):
        return jsii.set(self, "provisioningParameters", value)

    @property
    @jsii.member(jsii_name="provisioningPreferences")
    def provisioning_preferences(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ProvisioningPreferencesProperty"]]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningPreferences``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences
        """
        return jsii.get(self, "provisioningPreferences")

    @provisioning_preferences.setter
    def provisioning_preferences(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ProvisioningPreferencesProperty"]]]):
        return jsii.set(self, "provisioningPreferences", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class ProvisioningParameterProperty():
        def __init__(self, *, key: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param key: ``CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty.Key``.
            :param value: ``CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningparameter.html
            """
            self._values = {
            }
            if key is not None: self._values["key"] = key
            if value is not None: self._values["value"] = value

        @property
        def key(self) -> typing.Optional[str]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningparameter.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningparameter-key
            """
            return self._values.get('key')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningparameter.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningparameter-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProvisioningParameterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty", jsii_struct_bases=[], name_mapping={'stack_set_accounts': 'stackSetAccounts', 'stack_set_failure_tolerance_count': 'stackSetFailureToleranceCount', 'stack_set_failure_tolerance_percentage': 'stackSetFailureTolerancePercentage', 'stack_set_max_concurrency_count': 'stackSetMaxConcurrencyCount', 'stack_set_max_concurrency_percentage': 'stackSetMaxConcurrencyPercentage', 'stack_set_operation_type': 'stackSetOperationType', 'stack_set_regions': 'stackSetRegions'})
    class ProvisioningPreferencesProperty():
        def __init__(self, *, stack_set_accounts: typing.Optional[typing.List[str]]=None, stack_set_failure_tolerance_count: typing.Optional[jsii.Number]=None, stack_set_failure_tolerance_percentage: typing.Optional[jsii.Number]=None, stack_set_max_concurrency_count: typing.Optional[jsii.Number]=None, stack_set_max_concurrency_percentage: typing.Optional[jsii.Number]=None, stack_set_operation_type: typing.Optional[str]=None, stack_set_regions: typing.Optional[typing.List[str]]=None):
            """
            :param stack_set_accounts: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetAccounts``.
            :param stack_set_failure_tolerance_count: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetFailureToleranceCount``.
            :param stack_set_failure_tolerance_percentage: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetFailureTolerancePercentage``.
            :param stack_set_max_concurrency_count: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetMaxConcurrencyCount``.
            :param stack_set_max_concurrency_percentage: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetMaxConcurrencyPercentage``.
            :param stack_set_operation_type: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetOperationType``.
            :param stack_set_regions: ``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetRegions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html
            """
            self._values = {
            }
            if stack_set_accounts is not None: self._values["stack_set_accounts"] = stack_set_accounts
            if stack_set_failure_tolerance_count is not None: self._values["stack_set_failure_tolerance_count"] = stack_set_failure_tolerance_count
            if stack_set_failure_tolerance_percentage is not None: self._values["stack_set_failure_tolerance_percentage"] = stack_set_failure_tolerance_percentage
            if stack_set_max_concurrency_count is not None: self._values["stack_set_max_concurrency_count"] = stack_set_max_concurrency_count
            if stack_set_max_concurrency_percentage is not None: self._values["stack_set_max_concurrency_percentage"] = stack_set_max_concurrency_percentage
            if stack_set_operation_type is not None: self._values["stack_set_operation_type"] = stack_set_operation_type
            if stack_set_regions is not None: self._values["stack_set_regions"] = stack_set_regions

        @property
        def stack_set_accounts(self) -> typing.Optional[typing.List[str]]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetAccounts``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetaccounts
            """
            return self._values.get('stack_set_accounts')

        @property
        def stack_set_failure_tolerance_count(self) -> typing.Optional[jsii.Number]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetFailureToleranceCount``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetfailuretolerancecount
            """
            return self._values.get('stack_set_failure_tolerance_count')

        @property
        def stack_set_failure_tolerance_percentage(self) -> typing.Optional[jsii.Number]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetFailureTolerancePercentage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetfailuretolerancepercentage
            """
            return self._values.get('stack_set_failure_tolerance_percentage')

        @property
        def stack_set_max_concurrency_count(self) -> typing.Optional[jsii.Number]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetMaxConcurrencyCount``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetmaxconcurrencycount
            """
            return self._values.get('stack_set_max_concurrency_count')

        @property
        def stack_set_max_concurrency_percentage(self) -> typing.Optional[jsii.Number]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetMaxConcurrencyPercentage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetmaxconcurrencypercentage
            """
            return self._values.get('stack_set_max_concurrency_percentage')

        @property
        def stack_set_operation_type(self) -> typing.Optional[str]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetOperationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetoperationtype
            """
            return self._values.get('stack_set_operation_type')

        @property
        def stack_set_regions(self) -> typing.Optional[typing.List[str]]:
            """``CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty.StackSetRegions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences-stacksetregions
            """
            return self._values.get('stack_set_regions')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProvisioningPreferencesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnCloudFormationProvisionedProductProps", jsii_struct_bases=[], name_mapping={'accept_language': 'acceptLanguage', 'notification_arns': 'notificationArns', 'path_id': 'pathId', 'product_id': 'productId', 'product_name': 'productName', 'provisioned_product_name': 'provisionedProductName', 'provisioning_artifact_id': 'provisioningArtifactId', 'provisioning_artifact_name': 'provisioningArtifactName', 'provisioning_parameters': 'provisioningParameters', 'provisioning_preferences': 'provisioningPreferences', 'tags': 'tags'})
class CfnCloudFormationProvisionedProductProps():
    def __init__(self, *, accept_language: typing.Optional[str]=None, notification_arns: typing.Optional[typing.List[str]]=None, path_id: typing.Optional[str]=None, product_id: typing.Optional[str]=None, product_name: typing.Optional[str]=None, provisioned_product_name: typing.Optional[str]=None, provisioning_artifact_id: typing.Optional[str]=None, provisioning_artifact_name: typing.Optional[str]=None, provisioning_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty"]]]]]=None, provisioning_preferences: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::ServiceCatalog::CloudFormationProvisionedProduct``.

        :param accept_language: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.AcceptLanguage``.
        :param notification_arns: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.NotificationArns``.
        :param path_id: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.PathId``.
        :param product_id: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductId``.
        :param product_name: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductName``.
        :param provisioned_product_name: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisionedProductName``.
        :param provisioning_artifact_id: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactId``.
        :param provisioning_artifact_name: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactName``.
        :param provisioning_parameters: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningParameters``.
        :param provisioning_preferences: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningPreferences``.
        :param tags: ``AWS::ServiceCatalog::CloudFormationProvisionedProduct.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html
        """
        self._values = {
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if notification_arns is not None: self._values["notification_arns"] = notification_arns
        if path_id is not None: self._values["path_id"] = path_id
        if product_id is not None: self._values["product_id"] = product_id
        if product_name is not None: self._values["product_name"] = product_name
        if provisioned_product_name is not None: self._values["provisioned_product_name"] = provisioned_product_name
        if provisioning_artifact_id is not None: self._values["provisioning_artifact_id"] = provisioning_artifact_id
        if provisioning_artifact_name is not None: self._values["provisioning_artifact_name"] = provisioning_artifact_name
        if provisioning_parameters is not None: self._values["provisioning_parameters"] = provisioning_parameters
        if provisioning_preferences is not None: self._values["provisioning_preferences"] = provisioning_preferences
        if tags is not None: self._values["tags"] = tags

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def notification_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.NotificationArns``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-notificationarns
        """
        return self._values.get('notification_arns')

    @property
    def path_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.PathId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-pathid
        """
        return self._values.get('path_id')

    @property
    def product_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-productid
        """
        return self._values.get('product_id')

    @property
    def product_name(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProductName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-productname
        """
        return self._values.get('product_name')

    @property
    def provisioned_product_name(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisionedProductName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisionedproductname
        """
        return self._values.get('provisioned_product_name')

    @property
    def provisioning_artifact_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningartifactid
        """
        return self._values.get('provisioning_artifact_id')

    @property
    def provisioning_artifact_name(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningArtifactName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningartifactname
        """
        return self._values.get('provisioning_artifact_name')

    @property
    def provisioning_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCloudFormationProvisionedProduct.ProvisioningParameterProperty"]]]]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningparameters
        """
        return self._values.get('provisioning_parameters')

    @property
    def provisioning_preferences(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCloudFormationProvisionedProduct.ProvisioningPreferencesProperty"]]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.ProvisioningPreferences``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-provisioningpreferences
        """
        return self._values.get('provisioning_preferences')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::ServiceCatalog::CloudFormationProvisionedProduct.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html#cfn-servicecatalog-cloudformationprovisionedproduct-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCloudFormationProvisionedProductProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnLaunchNotificationConstraint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnLaunchNotificationConstraint"):
    """A CloudFormation ``AWS::ServiceCatalog::LaunchNotificationConstraint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::LaunchNotificationConstraint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, notification_arns: typing.List[str], portfolio_id: str, product_id: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::LaunchNotificationConstraint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param notification_arns: ``AWS::ServiceCatalog::LaunchNotificationConstraint.NotificationArns``.
        :param portfolio_id: ``AWS::ServiceCatalog::LaunchNotificationConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::LaunchNotificationConstraint.ProductId``.
        :param accept_language: ``AWS::ServiceCatalog::LaunchNotificationConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::LaunchNotificationConstraint.Description``.
        """
        props = CfnLaunchNotificationConstraintProps(notification_arns=notification_arns, portfolio_id=portfolio_id, product_id=product_id, accept_language=accept_language, description=description)

        jsii.create(CfnLaunchNotificationConstraint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.List[str]:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.NotificationArns``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-notificationarns
        """
        return jsii.get(self, "notificationArns")

    @notification_arns.setter
    def notification_arns(self, value: typing.List[str]):
        return jsii.set(self, "notificationArns", value)

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: str):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnLaunchNotificationConstraintProps", jsii_struct_bases=[], name_mapping={'notification_arns': 'notificationArns', 'portfolio_id': 'portfolioId', 'product_id': 'productId', 'accept_language': 'acceptLanguage', 'description': 'description'})
class CfnLaunchNotificationConstraintProps():
    def __init__(self, *, notification_arns: typing.List[str], portfolio_id: str, product_id: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::LaunchNotificationConstraint``.

        :param notification_arns: ``AWS::ServiceCatalog::LaunchNotificationConstraint.NotificationArns``.
        :param portfolio_id: ``AWS::ServiceCatalog::LaunchNotificationConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::LaunchNotificationConstraint.ProductId``.
        :param accept_language: ``AWS::ServiceCatalog::LaunchNotificationConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::LaunchNotificationConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html
        """
        self._values = {
            'notification_arns': notification_arns,
            'portfolio_id': portfolio_id,
            'product_id': product_id,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if description is not None: self._values["description"] = description

    @property
    def notification_arns(self) -> typing.List[str]:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.NotificationArns``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-notificationarns
        """
        return self._values.get('notification_arns')

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-productid
        """
        return self._values.get('product_id')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchNotificationConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchnotificationconstraint.html#cfn-servicecatalog-launchnotificationconstraint-description
        """
        return self._values.get('description')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLaunchNotificationConstraintProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnLaunchRoleConstraint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnLaunchRoleConstraint"):
    """A CloudFormation ``AWS::ServiceCatalog::LaunchRoleConstraint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::LaunchRoleConstraint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, portfolio_id: str, product_id: str, role_arn: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::LaunchRoleConstraint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param portfolio_id: ``AWS::ServiceCatalog::LaunchRoleConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::LaunchRoleConstraint.ProductId``.
        :param role_arn: ``AWS::ServiceCatalog::LaunchRoleConstraint.RoleArn``.
        :param accept_language: ``AWS::ServiceCatalog::LaunchRoleConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::LaunchRoleConstraint.Description``.
        """
        props = CfnLaunchRoleConstraintProps(portfolio_id=portfolio_id, product_id=product_id, role_arn=role_arn, accept_language=accept_language, description=description)

        jsii.create(CfnLaunchRoleConstraint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: str):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnLaunchRoleConstraintProps", jsii_struct_bases=[], name_mapping={'portfolio_id': 'portfolioId', 'product_id': 'productId', 'role_arn': 'roleArn', 'accept_language': 'acceptLanguage', 'description': 'description'})
class CfnLaunchRoleConstraintProps():
    def __init__(self, *, portfolio_id: str, product_id: str, role_arn: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::LaunchRoleConstraint``.

        :param portfolio_id: ``AWS::ServiceCatalog::LaunchRoleConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::LaunchRoleConstraint.ProductId``.
        :param role_arn: ``AWS::ServiceCatalog::LaunchRoleConstraint.RoleArn``.
        :param accept_language: ``AWS::ServiceCatalog::LaunchRoleConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::LaunchRoleConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html
        """
        self._values = {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'role_arn': role_arn,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if description is not None: self._values["description"] = description

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-productid
        """
        return self._values.get('product_id')

    @property
    def role_arn(self) -> str:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-rolearn
        """
        return self._values.get('role_arn')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchRoleConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchroleconstraint.html#cfn-servicecatalog-launchroleconstraint-description
        """
        return self._values.get('description')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLaunchRoleConstraintProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnLaunchTemplateConstraint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnLaunchTemplateConstraint"):
    """A CloudFormation ``AWS::ServiceCatalog::LaunchTemplateConstraint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::LaunchTemplateConstraint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, portfolio_id: str, product_id: str, rules: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::LaunchTemplateConstraint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param portfolio_id: ``AWS::ServiceCatalog::LaunchTemplateConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::LaunchTemplateConstraint.ProductId``.
        :param rules: ``AWS::ServiceCatalog::LaunchTemplateConstraint.Rules``.
        :param accept_language: ``AWS::ServiceCatalog::LaunchTemplateConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::LaunchTemplateConstraint.Description``.
        """
        props = CfnLaunchTemplateConstraintProps(portfolio_id=portfolio_id, product_id=product_id, rules=rules, accept_language=accept_language, description=description)

        jsii.create(CfnLaunchTemplateConstraint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: str):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="rules")
    def rules(self) -> str:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.Rules``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-rules
        """
        return jsii.get(self, "rules")

    @rules.setter
    def rules(self, value: str):
        return jsii.set(self, "rules", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnLaunchTemplateConstraintProps", jsii_struct_bases=[], name_mapping={'portfolio_id': 'portfolioId', 'product_id': 'productId', 'rules': 'rules', 'accept_language': 'acceptLanguage', 'description': 'description'})
class CfnLaunchTemplateConstraintProps():
    def __init__(self, *, portfolio_id: str, product_id: str, rules: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::LaunchTemplateConstraint``.

        :param portfolio_id: ``AWS::ServiceCatalog::LaunchTemplateConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::LaunchTemplateConstraint.ProductId``.
        :param rules: ``AWS::ServiceCatalog::LaunchTemplateConstraint.Rules``.
        :param accept_language: ``AWS::ServiceCatalog::LaunchTemplateConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::LaunchTemplateConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html
        """
        self._values = {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'rules': rules,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if description is not None: self._values["description"] = description

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-productid
        """
        return self._values.get('product_id')

    @property
    def rules(self) -> str:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.Rules``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-rules
        """
        return self._values.get('rules')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::LaunchTemplateConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-launchtemplateconstraint.html#cfn-servicecatalog-launchtemplateconstraint-description
        """
        return self._values.get('description')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLaunchTemplateConstraintProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnPortfolio(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolio"):
    """A CloudFormation ``AWS::ServiceCatalog::Portfolio``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::Portfolio
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, display_name: str, provider_name: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::Portfolio``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param display_name: ``AWS::ServiceCatalog::Portfolio.DisplayName``.
        :param provider_name: ``AWS::ServiceCatalog::Portfolio.ProviderName``.
        :param accept_language: ``AWS::ServiceCatalog::Portfolio.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::Portfolio.Description``.
        :param tags: ``AWS::ServiceCatalog::Portfolio.Tags``.
        """
        props = CfnPortfolioProps(display_name=display_name, provider_name=provider_name, accept_language=accept_language, description=description, tags=tags)

        jsii.create(CfnPortfolio, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrPortfolioName")
    def attr_portfolio_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: PortfolioName
        """
        return jsii.get(self, "attrPortfolioName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::ServiceCatalog::Portfolio.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> str:
        """``AWS::ServiceCatalog::Portfolio.DisplayName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-displayname
        """
        return jsii.get(self, "displayName")

    @display_name.setter
    def display_name(self, value: str):
        return jsii.set(self, "displayName", value)

    @property
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> str:
        """``AWS::ServiceCatalog::Portfolio.ProviderName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-providername
        """
        return jsii.get(self, "providerName")

    @provider_name.setter
    def provider_name(self, value: str):
        return jsii.set(self, "providerName", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::Portfolio.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::Portfolio.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


class CfnPortfolioPrincipalAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioPrincipalAssociation"):
    """A CloudFormation ``AWS::ServiceCatalog::PortfolioPrincipalAssociation``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::PortfolioPrincipalAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, portfolio_id: str, principal_arn: str, principal_type: str, accept_language: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::PortfolioPrincipalAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param portfolio_id: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PortfolioId``.
        :param principal_arn: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalARN``.
        :param principal_type: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalType``.
        :param accept_language: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.AcceptLanguage``.
        """
        props = CfnPortfolioPrincipalAssociationProps(portfolio_id=portfolio_id, principal_arn=principal_arn, principal_type=principal_type, accept_language=accept_language)

        jsii.create(CfnPortfolioPrincipalAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="principalArn")
    def principal_arn(self) -> str:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalARN``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-principalarn
        """
        return jsii.get(self, "principalArn")

    @principal_arn.setter
    def principal_arn(self, value: str):
        return jsii.set(self, "principalArn", value)

    @property
    @jsii.member(jsii_name="principalType")
    def principal_type(self) -> str:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-principaltype
        """
        return jsii.get(self, "principalType")

    @principal_type.setter
    def principal_type(self, value: str):
        return jsii.set(self, "principalType", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioPrincipalAssociationProps", jsii_struct_bases=[], name_mapping={'portfolio_id': 'portfolioId', 'principal_arn': 'principalArn', 'principal_type': 'principalType', 'accept_language': 'acceptLanguage'})
class CfnPortfolioPrincipalAssociationProps():
    def __init__(self, *, portfolio_id: str, principal_arn: str, principal_type: str, accept_language: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::PortfolioPrincipalAssociation``.

        :param portfolio_id: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PortfolioId``.
        :param principal_arn: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalARN``.
        :param principal_type: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalType``.
        :param accept_language: ``AWS::ServiceCatalog::PortfolioPrincipalAssociation.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html
        """
        self._values = {
            'portfolio_id': portfolio_id,
            'principal_arn': principal_arn,
            'principal_type': principal_type,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def principal_arn(self) -> str:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalARN``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-principalarn
        """
        return self._values.get('principal_arn')

    @property
    def principal_type(self) -> str:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.PrincipalType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-principaltype
        """
        return self._values.get('principal_type')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioPrincipalAssociation.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioprincipalassociation.html#cfn-servicecatalog-portfolioprincipalassociation-acceptlanguage
        """
        return self._values.get('accept_language')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPortfolioPrincipalAssociationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnPortfolioProductAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioProductAssociation"):
    """A CloudFormation ``AWS::ServiceCatalog::PortfolioProductAssociation``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::PortfolioProductAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, portfolio_id: str, product_id: str, accept_language: typing.Optional[str]=None, source_portfolio_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::PortfolioProductAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param portfolio_id: ``AWS::ServiceCatalog::PortfolioProductAssociation.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::PortfolioProductAssociation.ProductId``.
        :param accept_language: ``AWS::ServiceCatalog::PortfolioProductAssociation.AcceptLanguage``.
        :param source_portfolio_id: ``AWS::ServiceCatalog::PortfolioProductAssociation.SourcePortfolioId``.
        """
        props = CfnPortfolioProductAssociationProps(portfolio_id=portfolio_id, product_id=product_id, accept_language=accept_language, source_portfolio_id=source_portfolio_id)

        jsii.create(CfnPortfolioProductAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: str):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="sourcePortfolioId")
    def source_portfolio_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.SourcePortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-sourceportfolioid
        """
        return jsii.get(self, "sourcePortfolioId")

    @source_portfolio_id.setter
    def source_portfolio_id(self, value: typing.Optional[str]):
        return jsii.set(self, "sourcePortfolioId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioProductAssociationProps", jsii_struct_bases=[], name_mapping={'portfolio_id': 'portfolioId', 'product_id': 'productId', 'accept_language': 'acceptLanguage', 'source_portfolio_id': 'sourcePortfolioId'})
class CfnPortfolioProductAssociationProps():
    def __init__(self, *, portfolio_id: str, product_id: str, accept_language: typing.Optional[str]=None, source_portfolio_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::PortfolioProductAssociation``.

        :param portfolio_id: ``AWS::ServiceCatalog::PortfolioProductAssociation.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::PortfolioProductAssociation.ProductId``.
        :param accept_language: ``AWS::ServiceCatalog::PortfolioProductAssociation.AcceptLanguage``.
        :param source_portfolio_id: ``AWS::ServiceCatalog::PortfolioProductAssociation.SourcePortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html
        """
        self._values = {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if source_portfolio_id is not None: self._values["source_portfolio_id"] = source_portfolio_id

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-productid
        """
        return self._values.get('product_id')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def source_portfolio_id(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioProductAssociation.SourcePortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioproductassociation.html#cfn-servicecatalog-portfolioproductassociation-sourceportfolioid
        """
        return self._values.get('source_portfolio_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPortfolioProductAssociationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioProps", jsii_struct_bases=[], name_mapping={'display_name': 'displayName', 'provider_name': 'providerName', 'accept_language': 'acceptLanguage', 'description': 'description', 'tags': 'tags'})
class CfnPortfolioProps():
    def __init__(self, *, display_name: str, provider_name: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::ServiceCatalog::Portfolio``.

        :param display_name: ``AWS::ServiceCatalog::Portfolio.DisplayName``.
        :param provider_name: ``AWS::ServiceCatalog::Portfolio.ProviderName``.
        :param accept_language: ``AWS::ServiceCatalog::Portfolio.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::Portfolio.Description``.
        :param tags: ``AWS::ServiceCatalog::Portfolio.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html
        """
        self._values = {
            'display_name': display_name,
            'provider_name': provider_name,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if description is not None: self._values["description"] = description
        if tags is not None: self._values["tags"] = tags

    @property
    def display_name(self) -> str:
        """``AWS::ServiceCatalog::Portfolio.DisplayName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-displayname
        """
        return self._values.get('display_name')

    @property
    def provider_name(self) -> str:
        """``AWS::ServiceCatalog::Portfolio.ProviderName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-providername
        """
        return self._values.get('provider_name')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::Portfolio.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::Portfolio.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-description
        """
        return self._values.get('description')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::ServiceCatalog::Portfolio.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolio.html#cfn-servicecatalog-portfolio-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPortfolioProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnPortfolioShare(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioShare"):
    """A CloudFormation ``AWS::ServiceCatalog::PortfolioShare``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::PortfolioShare
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, account_id: str, portfolio_id: str, accept_language: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::PortfolioShare``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param account_id: ``AWS::ServiceCatalog::PortfolioShare.AccountId``.
        :param portfolio_id: ``AWS::ServiceCatalog::PortfolioShare.PortfolioId``.
        :param accept_language: ``AWS::ServiceCatalog::PortfolioShare.AcceptLanguage``.
        """
        props = CfnPortfolioShareProps(account_id=account_id, portfolio_id=portfolio_id, accept_language=accept_language)

        jsii.create(CfnPortfolioShare, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioShare.AccountId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html#cfn-servicecatalog-portfolioshare-accountid
        """
        return jsii.get(self, "accountId")

    @account_id.setter
    def account_id(self, value: str):
        return jsii.set(self, "accountId", value)

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioShare.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html#cfn-servicecatalog-portfolioshare-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioShare.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html#cfn-servicecatalog-portfolioshare-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnPortfolioShareProps", jsii_struct_bases=[], name_mapping={'account_id': 'accountId', 'portfolio_id': 'portfolioId', 'accept_language': 'acceptLanguage'})
class CfnPortfolioShareProps():
    def __init__(self, *, account_id: str, portfolio_id: str, accept_language: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::PortfolioShare``.

        :param account_id: ``AWS::ServiceCatalog::PortfolioShare.AccountId``.
        :param portfolio_id: ``AWS::ServiceCatalog::PortfolioShare.PortfolioId``.
        :param accept_language: ``AWS::ServiceCatalog::PortfolioShare.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html
        """
        self._values = {
            'account_id': account_id,
            'portfolio_id': portfolio_id,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language

    @property
    def account_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioShare.AccountId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html#cfn-servicecatalog-portfolioshare-accountid
        """
        return self._values.get('account_id')

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::PortfolioShare.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html#cfn-servicecatalog-portfolioshare-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::PortfolioShare.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-portfolioshare.html#cfn-servicecatalog-portfolioshare-acceptlanguage
        """
        return self._values.get('accept_language')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPortfolioShareProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnResourceUpdateConstraint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnResourceUpdateConstraint"):
    """A CloudFormation ``AWS::ServiceCatalog::ResourceUpdateConstraint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::ResourceUpdateConstraint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, portfolio_id: str, product_id: str, tag_update_on_provisioned_product: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::ResourceUpdateConstraint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param portfolio_id: ``AWS::ServiceCatalog::ResourceUpdateConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::ResourceUpdateConstraint.ProductId``.
        :param tag_update_on_provisioned_product: ``AWS::ServiceCatalog::ResourceUpdateConstraint.TagUpdateOnProvisionedProduct``.
        :param accept_language: ``AWS::ServiceCatalog::ResourceUpdateConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::ResourceUpdateConstraint.Description``.
        """
        props = CfnResourceUpdateConstraintProps(portfolio_id=portfolio_id, product_id=product_id, tag_update_on_provisioned_product=tag_update_on_provisioned_product, accept_language=accept_language, description=description)

        jsii.create(CfnResourceUpdateConstraint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: str):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="tagUpdateOnProvisionedProduct")
    def tag_update_on_provisioned_product(self) -> str:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.TagUpdateOnProvisionedProduct``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-tagupdateonprovisionedproduct
        """
        return jsii.get(self, "tagUpdateOnProvisionedProduct")

    @tag_update_on_provisioned_product.setter
    def tag_update_on_provisioned_product(self, value: str):
        return jsii.set(self, "tagUpdateOnProvisionedProduct", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnResourceUpdateConstraintProps", jsii_struct_bases=[], name_mapping={'portfolio_id': 'portfolioId', 'product_id': 'productId', 'tag_update_on_provisioned_product': 'tagUpdateOnProvisionedProduct', 'accept_language': 'acceptLanguage', 'description': 'description'})
class CfnResourceUpdateConstraintProps():
    def __init__(self, *, portfolio_id: str, product_id: str, tag_update_on_provisioned_product: str, accept_language: typing.Optional[str]=None, description: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::ResourceUpdateConstraint``.

        :param portfolio_id: ``AWS::ServiceCatalog::ResourceUpdateConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::ResourceUpdateConstraint.ProductId``.
        :param tag_update_on_provisioned_product: ``AWS::ServiceCatalog::ResourceUpdateConstraint.TagUpdateOnProvisionedProduct``.
        :param accept_language: ``AWS::ServiceCatalog::ResourceUpdateConstraint.AcceptLanguage``.
        :param description: ``AWS::ServiceCatalog::ResourceUpdateConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html
        """
        self._values = {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'tag_update_on_provisioned_product': tag_update_on_provisioned_product,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language
        if description is not None: self._values["description"] = description

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-productid
        """
        return self._values.get('product_id')

    @property
    def tag_update_on_provisioned_product(self) -> str:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.TagUpdateOnProvisionedProduct``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-tagupdateonprovisionedproduct
        """
        return self._values.get('tag_update_on_provisioned_product')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-acceptlanguage
        """
        return self._values.get('accept_language')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::ResourceUpdateConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-resourceupdateconstraint.html#cfn-servicecatalog-resourceupdateconstraint-description
        """
        return self._values.get('description')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResourceUpdateConstraintProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnStackSetConstraint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnStackSetConstraint"):
    """A CloudFormation ``AWS::ServiceCatalog::StackSetConstraint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::StackSetConstraint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, account_list: typing.List[str], admin_role: str, description: str, execution_role: str, portfolio_id: str, product_id: str, region_list: typing.List[str], stack_instance_control: str, accept_language: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::StackSetConstraint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param account_list: ``AWS::ServiceCatalog::StackSetConstraint.AccountList``.
        :param admin_role: ``AWS::ServiceCatalog::StackSetConstraint.AdminRole``.
        :param description: ``AWS::ServiceCatalog::StackSetConstraint.Description``.
        :param execution_role: ``AWS::ServiceCatalog::StackSetConstraint.ExecutionRole``.
        :param portfolio_id: ``AWS::ServiceCatalog::StackSetConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::StackSetConstraint.ProductId``.
        :param region_list: ``AWS::ServiceCatalog::StackSetConstraint.RegionList``.
        :param stack_instance_control: ``AWS::ServiceCatalog::StackSetConstraint.StackInstanceControl``.
        :param accept_language: ``AWS::ServiceCatalog::StackSetConstraint.AcceptLanguage``.
        """
        props = CfnStackSetConstraintProps(account_list=account_list, admin_role=admin_role, description=description, execution_role=execution_role, portfolio_id=portfolio_id, product_id=product_id, region_list=region_list, stack_instance_control=stack_instance_control, accept_language=accept_language)

        jsii.create(CfnStackSetConstraint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="accountList")
    def account_list(self) -> typing.List[str]:
        """``AWS::ServiceCatalog::StackSetConstraint.AccountList``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-accountlist
        """
        return jsii.get(self, "accountList")

    @account_list.setter
    def account_list(self, value: typing.List[str]):
        return jsii.set(self, "accountList", value)

    @property
    @jsii.member(jsii_name="adminRole")
    def admin_role(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.AdminRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-adminrole
        """
        return jsii.get(self, "adminRole")

    @admin_role.setter
    def admin_role(self, value: str):
        return jsii.set(self, "adminRole", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.ExecutionRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-executionrole
        """
        return jsii.get(self, "executionRole")

    @execution_role.setter
    def execution_role(self, value: str):
        return jsii.set(self, "executionRole", value)

    @property
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-portfolioid
        """
        return jsii.get(self, "portfolioId")

    @portfolio_id.setter
    def portfolio_id(self, value: str):
        return jsii.set(self, "portfolioId", value)

    @property
    @jsii.member(jsii_name="productId")
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-productid
        """
        return jsii.get(self, "productId")

    @product_id.setter
    def product_id(self, value: str):
        return jsii.set(self, "productId", value)

    @property
    @jsii.member(jsii_name="regionList")
    def region_list(self) -> typing.List[str]:
        """``AWS::ServiceCatalog::StackSetConstraint.RegionList``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-regionlist
        """
        return jsii.get(self, "regionList")

    @region_list.setter
    def region_list(self, value: typing.List[str]):
        return jsii.set(self, "regionList", value)

    @property
    @jsii.member(jsii_name="stackInstanceControl")
    def stack_instance_control(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.StackInstanceControl``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-stackinstancecontrol
        """
        return jsii.get(self, "stackInstanceControl")

    @stack_instance_control.setter
    def stack_instance_control(self, value: str):
        return jsii.set(self, "stackInstanceControl", value)

    @property
    @jsii.member(jsii_name="acceptLanguage")
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::StackSetConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-acceptlanguage
        """
        return jsii.get(self, "acceptLanguage")

    @accept_language.setter
    def accept_language(self, value: typing.Optional[str]):
        return jsii.set(self, "acceptLanguage", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnStackSetConstraintProps", jsii_struct_bases=[], name_mapping={'account_list': 'accountList', 'admin_role': 'adminRole', 'description': 'description', 'execution_role': 'executionRole', 'portfolio_id': 'portfolioId', 'product_id': 'productId', 'region_list': 'regionList', 'stack_instance_control': 'stackInstanceControl', 'accept_language': 'acceptLanguage'})
class CfnStackSetConstraintProps():
    def __init__(self, *, account_list: typing.List[str], admin_role: str, description: str, execution_role: str, portfolio_id: str, product_id: str, region_list: typing.List[str], stack_instance_control: str, accept_language: typing.Optional[str]=None):
        """Properties for defining a ``AWS::ServiceCatalog::StackSetConstraint``.

        :param account_list: ``AWS::ServiceCatalog::StackSetConstraint.AccountList``.
        :param admin_role: ``AWS::ServiceCatalog::StackSetConstraint.AdminRole``.
        :param description: ``AWS::ServiceCatalog::StackSetConstraint.Description``.
        :param execution_role: ``AWS::ServiceCatalog::StackSetConstraint.ExecutionRole``.
        :param portfolio_id: ``AWS::ServiceCatalog::StackSetConstraint.PortfolioId``.
        :param product_id: ``AWS::ServiceCatalog::StackSetConstraint.ProductId``.
        :param region_list: ``AWS::ServiceCatalog::StackSetConstraint.RegionList``.
        :param stack_instance_control: ``AWS::ServiceCatalog::StackSetConstraint.StackInstanceControl``.
        :param accept_language: ``AWS::ServiceCatalog::StackSetConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html
        """
        self._values = {
            'account_list': account_list,
            'admin_role': admin_role,
            'description': description,
            'execution_role': execution_role,
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'region_list': region_list,
            'stack_instance_control': stack_instance_control,
        }
        if accept_language is not None: self._values["accept_language"] = accept_language

    @property
    def account_list(self) -> typing.List[str]:
        """``AWS::ServiceCatalog::StackSetConstraint.AccountList``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-accountlist
        """
        return self._values.get('account_list')

    @property
    def admin_role(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.AdminRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-adminrole
        """
        return self._values.get('admin_role')

    @property
    def description(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-description
        """
        return self._values.get('description')

    @property
    def execution_role(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.ExecutionRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-executionrole
        """
        return self._values.get('execution_role')

    @property
    def portfolio_id(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.PortfolioId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-portfolioid
        """
        return self._values.get('portfolio_id')

    @property
    def product_id(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.ProductId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-productid
        """
        return self._values.get('product_id')

    @property
    def region_list(self) -> typing.List[str]:
        """``AWS::ServiceCatalog::StackSetConstraint.RegionList``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-regionlist
        """
        return self._values.get('region_list')

    @property
    def stack_instance_control(self) -> str:
        """``AWS::ServiceCatalog::StackSetConstraint.StackInstanceControl``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-stackinstancecontrol
        """
        return self._values.get('stack_instance_control')

    @property
    def accept_language(self) -> typing.Optional[str]:
        """``AWS::ServiceCatalog::StackSetConstraint.AcceptLanguage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-stacksetconstraint.html#cfn-servicecatalog-stacksetconstraint-acceptlanguage
        """
        return self._values.get('accept_language')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnStackSetConstraintProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnTagOption(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnTagOption"):
    """A CloudFormation ``AWS::ServiceCatalog::TagOption``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::TagOption
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, key: str, value: str, active: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::ServiceCatalog::TagOption``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param key: ``AWS::ServiceCatalog::TagOption.Key``.
        :param value: ``AWS::ServiceCatalog::TagOption.Value``.
        :param active: ``AWS::ServiceCatalog::TagOption.Active``.
        """
        props = CfnTagOptionProps(key=key, value=value, active=active)

        jsii.create(CfnTagOption, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="key")
    def key(self) -> str:
        """``AWS::ServiceCatalog::TagOption.Key``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html#cfn-servicecatalog-tagoption-key
        """
        return jsii.get(self, "key")

    @key.setter
    def key(self, value: str):
        return jsii.set(self, "key", value)

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> str:
        """``AWS::ServiceCatalog::TagOption.Value``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html#cfn-servicecatalog-tagoption-value
        """
        return jsii.get(self, "value")

    @value.setter
    def value(self, value: str):
        return jsii.set(self, "value", value)

    @property
    @jsii.member(jsii_name="active")
    def active(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::ServiceCatalog::TagOption.Active``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html#cfn-servicecatalog-tagoption-active
        """
        return jsii.get(self, "active")

    @active.setter
    def active(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "active", value)


class CfnTagOptionAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicecatalog.CfnTagOptionAssociation"):
    """A CloudFormation ``AWS::ServiceCatalog::TagOptionAssociation``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoptionassociation.html
    cloudformationResource:
    :cloudformationResource:: AWS::ServiceCatalog::TagOptionAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_id: str, tag_option_id: str) -> None:
        """Create a new ``AWS::ServiceCatalog::TagOptionAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param resource_id: ``AWS::ServiceCatalog::TagOptionAssociation.ResourceId``.
        :param tag_option_id: ``AWS::ServiceCatalog::TagOptionAssociation.TagOptionId``.
        """
        props = CfnTagOptionAssociationProps(resource_id=resource_id, tag_option_id=tag_option_id)

        jsii.create(CfnTagOptionAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """``AWS::ServiceCatalog::TagOptionAssociation.ResourceId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoptionassociation.html#cfn-servicecatalog-tagoptionassociation-resourceid
        """
        return jsii.get(self, "resourceId")

    @resource_id.setter
    def resource_id(self, value: str):
        return jsii.set(self, "resourceId", value)

    @property
    @jsii.member(jsii_name="tagOptionId")
    def tag_option_id(self) -> str:
        """``AWS::ServiceCatalog::TagOptionAssociation.TagOptionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoptionassociation.html#cfn-servicecatalog-tagoptionassociation-tagoptionid
        """
        return jsii.get(self, "tagOptionId")

    @tag_option_id.setter
    def tag_option_id(self, value: str):
        return jsii.set(self, "tagOptionId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnTagOptionAssociationProps", jsii_struct_bases=[], name_mapping={'resource_id': 'resourceId', 'tag_option_id': 'tagOptionId'})
class CfnTagOptionAssociationProps():
    def __init__(self, *, resource_id: str, tag_option_id: str):
        """Properties for defining a ``AWS::ServiceCatalog::TagOptionAssociation``.

        :param resource_id: ``AWS::ServiceCatalog::TagOptionAssociation.ResourceId``.
        :param tag_option_id: ``AWS::ServiceCatalog::TagOptionAssociation.TagOptionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoptionassociation.html
        """
        self._values = {
            'resource_id': resource_id,
            'tag_option_id': tag_option_id,
        }

    @property
    def resource_id(self) -> str:
        """``AWS::ServiceCatalog::TagOptionAssociation.ResourceId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoptionassociation.html#cfn-servicecatalog-tagoptionassociation-resourceid
        """
        return self._values.get('resource_id')

    @property
    def tag_option_id(self) -> str:
        """``AWS::ServiceCatalog::TagOptionAssociation.TagOptionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoptionassociation.html#cfn-servicecatalog-tagoptionassociation-tagoptionid
        """
        return self._values.get('tag_option_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnTagOptionAssociationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-servicecatalog.CfnTagOptionProps", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value', 'active': 'active'})
class CfnTagOptionProps():
    def __init__(self, *, key: str, value: str, active: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
        """Properties for defining a ``AWS::ServiceCatalog::TagOption``.

        :param key: ``AWS::ServiceCatalog::TagOption.Key``.
        :param value: ``AWS::ServiceCatalog::TagOption.Value``.
        :param active: ``AWS::ServiceCatalog::TagOption.Active``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html
        """
        self._values = {
            'key': key,
            'value': value,
        }
        if active is not None: self._values["active"] = active

    @property
    def key(self) -> str:
        """``AWS::ServiceCatalog::TagOption.Key``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html#cfn-servicecatalog-tagoption-key
        """
        return self._values.get('key')

    @property
    def value(self) -> str:
        """``AWS::ServiceCatalog::TagOption.Value``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html#cfn-servicecatalog-tagoption-value
        """
        return self._values.get('value')

    @property
    def active(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::ServiceCatalog::TagOption.Active``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-tagoption.html#cfn-servicecatalog-tagoption-active
        """
        return self._values.get('active')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnTagOptionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnAcceptedPortfolioShare", "CfnAcceptedPortfolioShareProps", "CfnCloudFormationProduct", "CfnCloudFormationProductProps", "CfnCloudFormationProvisionedProduct", "CfnCloudFormationProvisionedProductProps", "CfnLaunchNotificationConstraint", "CfnLaunchNotificationConstraintProps", "CfnLaunchRoleConstraint", "CfnLaunchRoleConstraintProps", "CfnLaunchTemplateConstraint", "CfnLaunchTemplateConstraintProps", "CfnPortfolio", "CfnPortfolioPrincipalAssociation", "CfnPortfolioPrincipalAssociationProps", "CfnPortfolioProductAssociation", "CfnPortfolioProductAssociationProps", "CfnPortfolioProps", "CfnPortfolioShare", "CfnPortfolioShareProps", "CfnResourceUpdateConstraint", "CfnResourceUpdateConstraintProps", "CfnStackSetConstraint", "CfnStackSetConstraintProps", "CfnTagOption", "CfnTagOptionAssociation", "CfnTagOptionAssociationProps", "CfnTagOptionProps", "__jsii_assembly__"]

publication.publish()
