from troposphere.cloudformation import AWSCustomObject


class CustomCognitoDomain(AWSCustomObject):
    """
    Custom cloud-formation resource used to create a domain name for AWS Cognito user pool.
    """
    resource_type = "Custom::CognitoDomain"

    props = {
        'ServiceToken': (str, True),
        'UserPoolId': (str, True),
        'DomainName': (str, True),
    }
