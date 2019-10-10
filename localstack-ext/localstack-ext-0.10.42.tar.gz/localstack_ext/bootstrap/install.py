import os
import logging
import localstack
from localstack.utils.common import mkdir,run,new_tmp_file,rm_rf,download,unzip
LOG=logging.getLogger(__name__)
RULE_ENGINE_INSTALL_URL='https://github.com/whummer/serverless-iot-offline'
H2_DOWNLOAD_URL='http://www.h2database.com/h2-2019-03-13.zip'
INFRA_DIR=os.path.join(os.path.dirname(localstack.__file__),'infra')
LOCALSTACK_DIR=os.path.dirname(localstack.__file__)
def install_libs():
 install_iot_rule_engine()
 install_h2()
def install_iot_rule_engine():
 target_dir=LOCALSTACK_DIR
 main_file=os.path.join(target_dir,'node_modules','serverless-iot-offline','query.js')
 if not os.path.exists(main_file):
  LOG.info('Installing IoT rule engine. This may take a while.')
  run('cd %s; npm install %s'%(target_dir,RULE_ENGINE_INSTALL_URL))
 return main_file
def install_h2():
 target_dir=os.path.join(INFRA_DIR,'h2')
 if not os.path.exists(target_dir):
  mkdir(target_dir)
  zip_file=new_tmp_file()
  LOG.info('Downloading dependencies for RDS server. This may take a while.')
  download(H2_DOWNLOAD_URL,zip_file)
  unzip(zip_file,target_dir)
  rm_rf(zip_file)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
