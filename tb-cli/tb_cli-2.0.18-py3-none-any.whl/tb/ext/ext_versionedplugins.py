import semver
from cement.ext.ext_plugin import CementPluginHandler
from tb import version


class VersionedPluginsConfigHandler(CementPluginHandler):

    class Meta:
        """Handler meta-data."""
        label = 'versionedplugins'

    def _setup(self, app_obj):
        super()._setup(app_obj)

        for plugin in list(self.get_enabled_plugins()):
            config = self.app.config.get_section_dict(f'plugin.{plugin}')
            if config.get('min-version'):
                min_version = config.get('min-version')
                if semver.compare(version.__version__, min_version) == -1:
                    app_obj.log.debug(f"Disabling plugin {plugin} as it expects a more recent version of {min_version}")
                    self._enabled_plugins.remove(plugin)
                    self._disabled_plugins.append(plugin)


def load(app):
    app.handler.register(VersionedPluginsConfigHandler)
