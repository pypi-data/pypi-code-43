import shutil
import os
def clear_dir(dir_name):
    if os.path.exists(dir_name) == True:
        shutil.rmtree(dir_name)
        os.makedirs(dir_name)
    else:
        os.makedirs(dir_name)

def clean_dir(dir_name):
    if os.path.exists(dir_name) == True:
        shutil.rmtree(dir_name)
        
    else:
        pass

def refresh():
    clean_dir('./data')
    shutil.copytree('./data_reference', './data')
    clear_dir('./work')
    clear_dir('./out')
    os.makedirs('./out/pic')
def delete(my_file):
    if os.path.exists(my_file): 
        os.remove(my_file) 
    else:
        pass
def get_name(paths):
    for num in range(len(paths)):
        if paths[num]=='/':
            pos = num
        else:
            pass
    name = paths[pos:]
    return name
import os
def remove_file(paths):
    if os.path.exists(paths):
        os.remove(paths)
    else:
        print("The file does not exist")