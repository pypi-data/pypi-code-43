import os
import sys
import subprocess
import argparse

EMPOWER_BATCH_INSTALL_ROOT_DIR = 'C:\Program Files\Metapraxis'
EMPOWER_BATCH_CONSOLE_EXE = 'Empower Batch Console.exe'

def execute_WindowsCmd(command_string,args=[]):
    
    if args==[]:
        p = subprocess.Popen(command_string, shell=True, stdout = subprocess.PIPE)
    else:
        p = subprocess.Popen([command_string]+args, shell=True, stdout = subprocess.PIPE)
    
    stdout, stderr = p.communicate()
    
    return p.returncode,stdout,stderr  

def execute_file_at_EBConsole(exe,script,site,user,password):
    
    #ret, stdout, stderr = execute_WindowsCmd(exe,[script,site,user,password])
    ret, stdout, stderr = execute_WindowsCmd('"{}" -f "{}" -s "{}" -u "{}" -p "{}"'.format(exe,script,site,user,password))
    
    return ret, stdout, stderr

   
if __name__ == '__main__':

    site_file_path = 'C:\Empower Sites\SampleSales03\SampleSales03.eks'
    user = ' Supervisor'
    password = 'super'
    
    versions_to_test = ['9.2','9.3']
    exe_path_list = [os.path.join(EMPOWER_BATCH_INSTALL_ROOT_DIR,'{}{}'.format('Empower ',f),EMPOWER_BATCH_CONSOLE_EXE) for f in versions_to_test]
    version_dict = dict(zip(versions_to_test,exe_path_list))
    
    script_dir = os.path.join(sys.path[0],'template')
    script_list = os.listdir(script_dir)
    script_path_list = [os.path.join(script_dir,f) for f in script_list]
    script_dict = dict(zip(script_list,script_path_list))
    
    for x in version_dict:
        
        for y in script_dict:
            
            ret, stdout, stderr = execute_file_at_EBConsole(version_dict[x],script_dict[y],site_file_path,user,password)
            
            print (x,y,ret)