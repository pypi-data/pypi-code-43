from zope import interface

class ISparcYamlConfigContainers(interface.Interface):
    def containers(yaml_config, base_dir=None, render_context=None):
        """Generator of sparc.config.IConfigContainer providers
        
        Args:
            yaml_config: Unicode valid file path to a Yaml configuration or a 
                         valid Yaml content string.
            base_dir: Unicode directory name that serves as reference point 
                      for relative yaml include tags (!include).  If yaml_config
                      is a file path, then this defaults to the hosting 
                      directory 
            render_context: A mapping that will be used as the context for
                            template rendering.
        """
    def first(yaml_config, base_dir=None, render_context=None):
        """first sparc.config.IConfigContainer provider in yaml_config
        
        Args:
            yaml_config: [same as documents()]
            base_dir: [same as documents()]
            render_context: [same as documents()]
        """