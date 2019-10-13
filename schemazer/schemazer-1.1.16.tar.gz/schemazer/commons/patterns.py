EmptyFormat = '^$'
IntegerFormat = '^[1-9]{1}[0-9]{0,10}$'
BooleanFormat = '^((True)|(False)|(true)|(false)|(0)|(1))$'
FloatFormat = '^[-+]?[0-9]*\.?[0-9]+$'
TextFormat = '^[^~!@#$%^&*\(\)_+0-9]{2,128}$'
PositiveFormat = '^[0-9]{0,10}$'
BigPositiveFormat = '^[0-9]{1,32}$'
ParagraphFormat = '^.{2,1000}$'
UUIDFormat = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-' \
             '[0-9a-f]{12}$'

PhoneFormat = '^(\+7)[0-9]{10}$'
PasswordFormat = '^\S{6,64}$'
EmailFormat = '^(?:[a-z0-9_-]+(?:\.[a-z0-9!#$%&\'*+/=?^_' \
              '`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-' \
              '\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9]' \
              '(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?' \
              '|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}' \
              '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:' \
              '(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-' \
              '\x09\x0b\x0c\x0e-\x7f])+)\])$'
TokenFormat = '^[a-f0-9]{128}$'
SecretKeyFormat = '^[0-9]{6}$'
LoginFormat = '^[a-zA-Z0-9_-]{3,16}$'
ApiKeyFormat = '.{3,16}$'

BaseFormat = '^.+$'
QueryFormat = '^[\S -]{2,64}$'
