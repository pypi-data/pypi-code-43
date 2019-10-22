import os
import configparser


def getConfig(file_path, section='', option=''):
    result = None
    data = {}
    if os.path.exists( os.path.join( os.getcwd(),config_path ) ):
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")
        sections = config.sections()
        for section_item in sections:
            tmp = {}
            options = config.options(section_item)
            for option_item in options:
                tmp[option_item] = config.get(section_item,option_item)
            data[section_item] = tmp
    if section:
        if option:
            result = data[section][option]
        else:
            result = data[section]
    else:
        result = data
    return result

def setConfig(file_path,sections):
    conf = configparser.ConfigParser()
    cfgfile = open(file_path,'w')
    for section in sections:
        conf.add_section(section)
        for option in sections[section]:
            conf.set(section, option, sections[section][option])
    conf.write(cfgfile)
    cfgfile.close()