
from dl_rank.file.file_api import pathStr
from dl_rank.file.wfile import wfile
import os
from tensorflow import gfile

def copy_conf2logpath(conf_dir, save_path):
    conf_dir = pathStr(conf_dir)
    conf_path, conf_name = conf_dir.rsplit('/', 1)
    out_path = pathStr(conf_name, prefix=save_path)
    if not wfile.Exists(out_path):
        wfile.MakeDirs(out_path)
    wfile.CopyDirectory(conf_dir, out_path, overwrite=True)
    return out_path



def getConfInfo(confDir):
    if confDir[-1] == '/':
        confDir = confDir[:-1]
    if confDir.startswith('s3'):
        return confDir, confDir
    else:
        confDir = os.path.abspath(confDir)
        confName = confDir.rsplit('/', 1)[1]
    return confName, confDir



def find_conf(conf, save_path):
    if conf.startswith('s3'):
        conf = conf.strip('/')
        conf_name = conf.rsplit('/', 1)[1]
        save_path = os.path.join(save_path, conf_name) + '/'
        gfile.MakeDirs(save_path)
        check = os.system('aws s3 cp {} {} --recursive'.format(conf+'/', save_path))
        conf = save_path
        if check:
            assert False, 'cant find conf in: {}'.format(conf)
        return conf
    conf_path = os.path.abspath(conf)
    return conf_path