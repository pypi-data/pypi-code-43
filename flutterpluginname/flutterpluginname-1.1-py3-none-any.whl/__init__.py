from .utils import *
import fire
import os
import shutil
from pathlib import Path
import json
import yaml


def read_plugin_class_name_from_pubspec(pubspec_path):
    pubspec_dict = yaml.load(open(pubspec_path), Loader=yaml.FullLoader)
    iosPrefix = ''
    if "iosPrefix" in pubspec_dict["flutter"]["plugin"]:
        iosPrefix = pubspec_dict["flutter"]["plugin"]["iosPrefix"]
    return iosPrefix + pubspec_dict["flutter"]["plugin"]["pluginClass"]

def fetch_flutter_plugin_list(root_path):
    # read plugin paths
    flutter_plugin_file = os.path.join(root_path, ".flutter-plugins")
    flutter_plugin_paths = {}
    flutter_plugin_class_names = {}
    with open(flutter_plugin_file) as file:
        lines = file.readlines()
        for line in lines:
            pair = line.split("=")
            flutter_plugin_paths[pair[0]] = pair[1].strip("\n ")
    for name in flutter_plugin_paths.keys():
        path = os.path.join(flutter_plugin_paths[name], "pubspec.yaml")
        plugin_class_name = read_plugin_class_name_from_pubspec(path)
        flutter_plugin_class_names[name] = plugin_class_name

    return flutter_plugin_class_names

class FlutterPluginClassNameFetcher(object):
    def list(self, root_path="./", json_output_filename=".flutter_plugin_classes.json"):
        json_output_path = os.path.join(root_path, json_output_filename)
        if json_output_filename.startswith("/"):
            json_output_path = json_output_filename
        plugin_list = fetch_flutter_plugin_list(root_path)
        if os.path.exists(json_output_path):
            os.system("rm -rf {0}".format(json_output_path))
        plugin_list_json_str = json.dumps(plugin_list)
        with open(json_output_path, 'w+') as file:
            file.write(plugin_list_json_str)
        print(plugin_list_json_str)

    def gencode(self, root_path="./", code_output_filename="FlutterPlugins.h"):
        code_output_path = os.path.join(root_path, code_output_filename)
        if code_output_filename.startswith("/"):
            code_output_path = code_output_filename
        plugin_list = fetch_flutter_plugin_list(root_path)
        code_template = '''
#define RegisterFlutterPlugins \\
{0}
        '''
        plugin_codes = ''
        for class_name in plugin_list.values():
            if class_name == list(plugin_list.values())[-1]:
                tpl = '[FLTPluginManager registerPluginClass:NSClassFromString(@"{0}")];\n'
            else:
                tpl = '[FLTPluginManager registerPluginClass:NSClassFromString(@"{0}")];\\\n'
            plugin_codes += tpl.format(class_name)
        codes = code_template.format(plugin_codes)
        with open(code_output_path, 'w+') as file:
            file.write(codes)


fire.Fire(FlutterPluginClassNameFetcher)