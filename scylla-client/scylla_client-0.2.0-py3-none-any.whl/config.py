from sitri import Sitri
from sitri.contrib.system import SystemConfigProvider, SystemCredentialProvider

conf = Sitri(
    config_provider=SystemConfigProvider(prefix="scylla"), credential_provider=SystemCredentialProvider(prefix="scylla")
)
