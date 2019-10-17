import os
import shutil


class Template(object):

    @staticmethod
    def copy_config_files(experiment_path):
        module_path = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(module_path, '../template')
        for filename in os.listdir(template_dir):
            src_config = os.path.join(template_dir, filename)
            dest_config = os.path.join(experiment_path, '%s' % filename)
            shutil.copy2(src_config, dest_config)
