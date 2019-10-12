from ingaia.commons.exceptions import GenericException


class IngaiaRLTokenNotDefinedException(GenericException):
    message = 'Define the environment variable "INGAIA_RL_TOKEN" in "app.yaml".'
