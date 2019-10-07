from troposphere.cloudformation import AWSCustomObject


class CustomCognitoClientSecret(AWSCustomObject):
    """
    Custom cloud-formation resource used to retrieve AWS Cognito user pool client secret.
    """
    resource_type = "Custom::CognitoClientSecret"

    props = {
        'ServiceToken': (str, True),
        'UserPoolId': (str, True),
        'ClientId': (str, True),
    }
