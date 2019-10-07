from troposphere.cloudformation import AWSCustomObject


class CustomCognitoFacebook(AWSCustomObject):
    """
    Custom cloud-formation resource used to create a facebook identity provider for AWS Cognito user pool.
    """
    resource_type = "Custom::CognitoFacebook"

    props = {
        'ServiceToken': (str, True),
        'UserPoolId': (str, True),
        'FacebookClientId': (str, True),
        'FacebookClientSecret': (str, True),
    }
