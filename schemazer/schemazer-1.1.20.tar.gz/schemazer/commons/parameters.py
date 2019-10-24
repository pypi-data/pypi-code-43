from schemazer.base import SchemazerParameter, SchemazerSystemParameter
from schemazer.commons.patterns import (PhoneFormat, EmailFormat,
                                        PasswordFormat, SecretKeyFormat,
                                        TokenFormat, ApiKeyFormat,
                                        BigPositiveFormat, BaseFormat,
                                        FloatFormat, BooleanFormat)
from schemazer.validator import PatternValidator


class BaseParameters:
    class Integer(SchemazerParameter):
        name = 'number'
        description = 'Number'
        type = int
        required = False
        example = '125'
        validator = PatternValidator(BigPositiveFormat)

    class String(SchemazerParameter):
        name = 'string'
        description = 'string'
        type = str
        required = False
        example = 'string'
        validator = PatternValidator(BaseFormat)

    class Float(SchemazerParameter):
        name = 'float'
        description = 'float'
        type = float
        required = False
        example = 123.123
        validator = PatternValidator(FloatFormat)

    class Boolean(SchemazerParameter):
        name = 'bool'
        description = 'bool'
        type = bool
        required = False
        example = True
        validator = PatternValidator(BooleanFormat)


class AuthParameters:
    class Phone(SchemazerParameter):
        name = 'phone'
        description = 'Number of phone'
        type = str
        required = True
        example = '81234567890'
        validator = PatternValidator(PhoneFormat)

    class Email(SchemazerParameter):
        name = 'email'
        description = 'Email'
        type = str
        required = True
        example = 'example@gmail.ru'
        validator = PatternValidator(EmailFormat)

    class Password(SchemazerParameter):
        name = 'password'
        description = 'Password'
        type = str
        required = True
        example = 'kf7J73nsIJN'
        validator = PatternValidator(PasswordFormat)

    class SecretKey(SchemazerParameter):
        name = 'secret_key'
        description = 'Secret key parameter'
        type = str
        required = True
        example = '9845121'
        validator = PatternValidator(SecretKeyFormat)

    class Token(SchemazerParameter):
        name = 'token'
        description = 'Registration token'
        type = str
        required = True
        example = '202cb962ac59075b964b07152d234b70'
        validator = PatternValidator(TokenFormat)

    class ApiKey(SchemazerParameter):
        name = 'apikey'
        description = 'Api secret key'
        type = str
        required = True
        example = '202cb962ac59075b'
        validator = PatternValidator(ApiKeyFormat)


class SystemParameters:
    class Apikey(SchemazerSystemParameter):
        query_param = 'apikey'
        header_param = 'apikey'
        cookie_param = 'apikey'

        name = 'apikey'
        description = 'App apikey'
        type = str
        required = True
        example = '202cb962ac5907'
        validator = PatternValidator(ApiKeyFormat)
