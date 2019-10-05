import os
import re

from . import proputil
from . import system

# Global property keys
SEEQ_INSTALLATION_ID = "seeq_installation_id"
SEEQ_TELEMETRY_ENABLED = "seeq_telemetry_enabled"
SEEQ_SERVICE_MODE = "seeq_service_mode"
SEEQ_ADMIN_CONTACT_NAME = "seeq_admin_contact_name"
SEEQ_ADMIN_CONTACT_EMAIL = "seeq_admin_contact_email"
SEEQ_DATA_FOLDER = "seeq_data_folder"
SEEQ_BACKUP_FOLDER = "seeq_backup_folder"
SEEQ_STARTING_PORT = "seeq_starting_port"
SEEQ_SERVER_HOSTNAME = "seeq_server_hostname"
SEEQ_SERVER_PORT = "seeq_server_port"
SEEQ_SECURE_PORT = "seeq_secure_port"
SEEQ_INCOMING_ALLOWED_HOSTNAME = "seeq_incoming_allowed_hostname"
SEEQ_SERVER_TYPE = "seeq_server_type"

# Ports
APPSERVER_PORT = "appserverPort"
APPSERVER_JMX_PORT = "appserverJMXPort"
APPSERVER_DEBUG_PORT = "appserverDebugPort"
CASSANDRA_CQL_PORT = "cassandraCQLPort"
CASSANDRA_JMX_PORT = "cassandraJMXPort"
CASSANDRA_STORAGE_PORT = "cassandraStoragePort"
CASSANDRA_SSL_PORT = "cassandraSSLPort"
JVM_LINK_JMX_PORT = "JVMLinkJMXPort"
JVM_LINK_DEBUG_PORT = "JVMLinkDebugPort"
WEBSERVER_PRIMARY_PORT = "webserverPrimaryPort"
SUPERVISOR_UI_REST_PORT = "supervisorUIRESTPort"
SUPERVISOR_UI_SINGLE_INSTANCE_PORT = "supervisorUISingleInstancePort"
SUPERVISOR_UI_DEBUG_PORT = "supervisorUIDebugPort"
SUPERVISOR_CORE_REST_PORT = "supervisorCoreRESTPort"
SUPERVISOR_CORE_SINGLE_INSTANCE_PORT = "supervisorCoreSingleInstancePort"
SUPERVISOR_CORE_DEBUG_PORT = "supervisorCoreDebugPort"
IIS_PORT = "iisPort"
IGNITION_DEBUG_PORT = "ignitionDebugPort"
POSTGRES_PORT = "postgresPort"

# Used by cassandra, appserver, and jvm-link; for running in development all the security features turned off
INSECURE_JVM_JMX_OPTIONS = ' '.join([
    '-Dcom.sun.management.jmxremote.authenticate=false',
    '-Dcom.sun.management.jmxremote.ssl=false'
])

ENVIRONMENT_DEV = 'dev'
ENVIRONMENT_PROD = 'prod'

g_seeq_environment = ENVIRONMENT_DEV
g_seeq_global_properties_override = {}
g_seeq_global_folder_override = None


def set_seeq_environment(env):
    global g_seeq_environment
    g_seeq_environment = env


def get_seeq_environment():
    global g_seeq_environment
    return g_seeq_environment


def get_seeq_global_properties_override():
    global g_seeq_global_properties_override
    return g_seeq_global_properties_override


def is_dev():
    return g_seeq_environment == ENVIRONMENT_DEV


def get_global_folder():
    """
    Returns the location of the "global" folder that contains the global properties file, licenses and is the default
    location for the data folder. It is C:\ProgramData\Seeq on Windows, ~/.seeq on UNIX.

    It can be overridden in Pilot commands with the "-g" root argument.

    It can be specified at install time using the "seeq install --global" flag, where it will be written to an
    install.properties file in the image folder.

    :return: Location of the global folder
    """
    global g_seeq_global_folder_override

    global_folder = get_property('seeq_global_folder', get_seeq_install_properties_file())
    if not global_folder:
        if system.is_windows():
            global_folder = os.path.join(os.environ["ProgramData"], 'Seeq')
        else:
            global_folder = os.path.join(system.get_home_dir(), '.seeq')

    if g_seeq_global_folder_override:
        global_folder = g_seeq_global_folder_override

    create_folder_if_necessary_with_correct_permissions(global_folder)

    return global_folder


def override_global_folder(global_folder_override):
    global g_seeq_global_folder_override

    g_seeq_global_folder_override = global_folder_override


def get_seeq_global_properties_file():
    """
    Returns the location of the machine-global properties file that is used for high-level configuration of the
    Seeq product. If not overridden, it is C:\ProgramData\Seeq\global.properties on Windows,
    ~/.seeq/global.properties on UNIX.

    :return: Location of the machine-global properties file
    """
    return os.path.join(get_global_folder(), 'global.properties')


def get_seeq_install_properties_file():
    return os.path.join(get_image_folder(), 'install.properties')


def get_seeq_hostname():
    hostname = 'localhost'
    if get_seeq_global_property(SEEQ_SERVER_HOSTNAME):
        hostname = get_seeq_global_property(SEEQ_SERVER_HOSTNAME)
    return hostname


def get_port(port):
    return get_ports()[port]


def get_ports():
    starting_port = 34210

    properties = get_seeq_global_properties()
    if SEEQ_STARTING_PORT in properties and len(properties[SEEQ_STARTING_PORT].strip()) > 0:
        starting_port = int(properties[SEEQ_STARTING_PORT])

    ports = {
        CASSANDRA_STORAGE_PORT: starting_port,
        CASSANDRA_SSL_PORT: starting_port + 1,
        JVM_LINK_JMX_PORT: starting_port + 2,
        CASSANDRA_JMX_PORT: starting_port + 3,
        CASSANDRA_CQL_PORT: starting_port + 4,
        # starting_port + 5 was previously used for CASSANDRA_THRIFT_PORT and later for ELASTICSEARCH_JMX_PORT
        POSTGRES_PORT: starting_port + 5,
        WEBSERVER_PRIMARY_PORT: starting_port + 6,
        # starting_port + 7 was previously used for webserver fast follow/socket io but is no longer used
        APPSERVER_PORT: starting_port + 8,
        SUPERVISOR_CORE_REST_PORT: starting_port + 9,
        SUPERVISOR_UI_REST_PORT: starting_port + 10,
        SUPERVISOR_CORE_SINGLE_INSTANCE_PORT: starting_port + 11,
        SUPERVISOR_UI_SINGLE_INSTANCE_PORT: starting_port + 12,
        APPSERVER_JMX_PORT: starting_port + 13,
        # starting_port + 14 was previously used for ELASTICSEARCH_REST_PORT but is no longer used
        # starting_port + 15 was previously used for ELASTICSEARCH_NODE_PORT but is no longer used
        IIS_PORT: starting_port + 16,
        APPSERVER_DEBUG_PORT: starting_port + 17,
        JVM_LINK_DEBUG_PORT: starting_port + 18,
        SUPERVISOR_UI_DEBUG_PORT: starting_port + 19,
        SUPERVISOR_CORE_DEBUG_PORT: starting_port + 20}

    if SEEQ_SERVER_PORT in properties and len(properties[SEEQ_SERVER_PORT].strip()) > 0:
        ports[WEBSERVER_PRIMARY_PORT] = int(properties[SEEQ_SERVER_PORT])

    if SEEQ_SECURE_PORT in properties and len(properties[SEEQ_SECURE_PORT].strip()) > 0:
        ports[WEBSERVER_PRIMARY_PORT] = int(properties[SEEQ_SECURE_PORT])

    # These ports are static and unmoving, they are developer-only ports
    ports[IGNITION_DEBUG_PORT] = 34240

    return ports


def override_global_property(prop, value):
    global g_seeq_global_properties_override
    if value is None:
        if prop in g_seeq_global_properties_override:
            del g_seeq_global_properties_override[prop]
    else:
        g_seeq_global_properties_override[prop] = value


def get_seeq_global_properties():
    properties = get_properties(get_seeq_global_properties_file())

    global g_seeq_global_properties_override
    properties.update(g_seeq_global_properties_override)

    return properties


def get_properties(properties_file):
    """
    Retrieves all properties from a properties file.
    :param properties_file: Properties file to use
    :return: A dictionary of property name-values.
    """
    properties = {}

    if not os.path.exists(properties_file):
        return properties

    properties = proputil.get_properties(properties_file)

    return properties


def get_seeq_global_property(property_name):
    global_properties = get_seeq_global_properties()
    return global_properties[property_name] if property_name in global_properties else ''


def get_property(property_name, properties_file):
    """
    Retrieves a property from the machine-global properties file.
    :param property_name: Name of the property to retrieve.
    :param properties_file: Properties file to use
    :return: The value of the property. Will be a blank string ('') if the property is not set or the file does not exist.
    """
    properties = get_properties(properties_file)

    if property_name not in properties:
        return ''

    return properties[property_name]


def set_seeq_global_property(property_name, property_value):
    fix_permissions = False
    if not os.path.exists(get_seeq_global_properties_file()):
        fix_permissions = True

    set_property(property_name, property_value, get_seeq_global_properties_file())

    if fix_permissions:
        system.fix_permissions(get_seeq_global_properties_file())


def set_property(property_name, property_value, properties_file):
    """
    Sets a property in the machine-global properties file.
    :param property_name: Name of the property to set.
    :param properties_file: Properties file to use
    :param property_value: Value of the property.
    """
    properties = get_properties(properties_file)
    properties[property_name] = property_value

    # See comment in propertiesutil.get_properties about why we don't use the pyjavaproperties library.
    lines = []
    for key, value in properties.items():
        lines.append("%s=%s" % (key, value))

    properties_dir = os.path.dirname(properties_file)
    if not os.path.exists(properties_dir):
        os.makedirs(properties_dir)

    lines.sort()

    with open(properties_file, 'w') as f:
        f.writelines(line + '\n' for line in lines)


def check_telemetry_enabled():
    """
    This utility function is called from various sites in the build script, usually when it's likely that AppServer
    is being run. The point is to make sure that the developer is purposefully enabling telemetry, and doesn't
    accidentally leave it on.
    """
    if get_seeq_global_property(SEEQ_TELEMETRY_ENABLED) == '':
        # If it has never been set, then set it to false (on a developer's machine).
        set_seeq_global_property(SEEQ_TELEMETRY_ENABLED, 'false')

    elif get_seeq_global_property(SEEQ_TELEMETRY_ENABLED) == 'true':
        print('************************************************************************************')
        print('')
        print('  HEY!')
        print('')
        print('Telemetry is enabled on your machine in %s' % get_seeq_global_properties_file())
        print('')
        print("Only do this if you're testing the telemetry feature. Otherwise you're polluting")
        print('our telemetry database with developer activity.')
        print('')
        print('************************************************************************************')


def create_folder_if_necessary_with_correct_permissions(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        system.fix_permissions(folder)


def get_data_folder():
    seeq_folder = get_global_folder()  # This will ensure the Seeq folder exists no matter what

    data_folder = None
    try:
        data_folder = get_dev_data_folder()
    except BaseException:
        pass

    if not data_folder:
        # Check if the data directory has been configured to a different location
        data_folder = get_seeq_global_property(SEEQ_DATA_FOLDER)
        if not data_folder:
            data_folder = os.path.join(seeq_folder, 'data')

    create_folder_if_necessary_with_correct_permissions(data_folder)

    return data_folder


def set_data_folder(data_folder):
    return set_seeq_global_property(SEEQ_DATA_FOLDER, data_folder)


def get_image_version():
    version_file = os.path.join(get_image_folder(), 'version.txt')
    if not os.path.exists(version_file):
        return None

    with open(version_file, 'r') as f:
        return f.read().strip()


def get_image_version_block():
    image_version = get_image_version()
    match = re.match(r'(\w+)\.(\d+)\.(\d+)\.(\d+)(-v\w+)?(-\w+)?', image_version)
    if not match:
        raise Exception('Unrecognized version string: %s' % image_version)

    version_block = dict()
    version_block['VERSION_PREFIX'] = match.group(1)
    version_block['VERSION_MAJOR'] = match.group(2)
    version_block['VERSION_MINOR'] = match.group(3)
    version_block['VERSION_PATCH'] = match.group(4)
    version_block['VERSION_DATETIME'] = match.group(5)
    version_block['VERSION_SUFFIX'] = match.group(6)

    return version_block


def get_data_version():
    version_file = os.path.join(get_data_folder(), 'version.txt')
    if not os.path.exists(version_file):
        return None

    with open(version_file, 'r') as f:
        return f.read().strip()


def get_dev_data_folder():
    return os.path.join(system.get_repo_root_dir(windows_long_path=False), 'sq-run-data-dir')


def get_image_folder():
    arch = 'x64'
    try:
        arch = system.get_build_architecture()
    except BaseException:
        # We're not executing from within the dev environment
        pass

    production_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    development_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'product', 'image', arch))

    return development_path if os.path.exists(development_path) else production_path


def get_service_exe():
    return os.path.join(get_image_folder(), 'SeeqService.exe')


def get_service_name():
    installation_name = get_property('seeq_installation_name', get_seeq_install_properties_file())
    return 'SeeqService' + ('_' + re.sub(r'\W', '_', installation_name) if installation_name else '')


def get_api_url():
    hostname = get_seeq_hostname()
    protocol = 'http'

    if get_seeq_global_property(SEEQ_SECURE_PORT):
        protocol = 'https'

    return '%s://%s:%d/api' % (protocol, hostname, get_port(WEBSERVER_PRIMARY_PORT))


def get_supervisor_core_properties_path():
    '''
    Retrieve the path to supervisor.properties.
    Will look first in the data folder, then the image folder.
    :return: The path to supervisor.properties or None if it's not found
    '''
    data_path = os.path.join(get_data_folder(), "configuration", "supervisor")
    image_path = os.path.join(get_image_folder(), "supervisor", "image", "configuration")

    filename = 'supervisor.core.properties'
    for path in (data_path, image_path):
        print('Looking for config file "%s" in "%s"' % (filename, path))
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            print('Using config file "%s' % filepath)
            return filepath

    return None


def get_supervisor_core_memory_multiplier():
    '''
    Get the value of the memory multiplier property from supervisor.core.properties.
    Default to 1.0 if the property cannot be found.
    :return: (float) the memory multiplier value.
    '''
    supervisor_properties_path = get_supervisor_core_properties_path()

    property_string = "memory.multiplier"
    memory_multiplier = None
    if not supervisor_properties_path:
        print("Could not find supervisor.properties.")
    else:
        memory_multiplier = proputil.get_property_from_config(property_string, supervisor_properties_path)

    try:
        memory_multiplier = float(memory_multiplier)
    except TypeError:
        print('Could not find property "%s" in "%s" ' % (property_string, supervisor_properties_path))
        memory_multiplier = 1.0
    except ValueError:
        print('Could not convert %s value "%s" to float' % (property_string, memory_multiplier))
        memory_multiplier = 1.0

    print("Using memory multiplier: %s" % memory_multiplier)

    return float(memory_multiplier)
