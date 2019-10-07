from cloudshell.cli.command_template.command_template import CommandTemplate


SET_STATUS_ENABLE = CommandTemplate('set status enable')

# SNMP V2
SHOW_V2_CONF = CommandTemplate('show system snmp community')

SET_COMMUNITY_NAME = CommandTemplate('set name {community}')
SET_V2C_STATUS_ENABLE = CommandTemplate('set query-v2c-status enable')

DELETE_SNMP_COMMUNITY = CommandTemplate('delete {community_id}')

# SNMP V3
SHOW_V3_CONF = CommandTemplate('show system snmp user')

# no-auth-no-priv | auth-no-priv | auth-priv
SET_SECURITY_LEVEL = CommandTemplate('set security-level {security_level}')
SET_AUTH_PROTO = CommandTemplate('set auth-proto {auth_type}')  # md5 | sha
SET_AUTH_PWD = CommandTemplate('set auth-pwd {password}')
# aes | des | aes256 | aes256cisco
SET_PRIV_PROTO = CommandTemplate('set priv-proto {priv_type}')
SET_PRIV_PWD = CommandTemplate('set priv-pwd {priv_key}')

DELETE_SNMP_USER = CommandTemplate('delete {user}')
