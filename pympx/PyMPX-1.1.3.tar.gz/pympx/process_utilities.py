import subprocess
import csv

# ------------------------------------
# set constants

def getProcessDictForImage():

    p_tasklist = subprocess.Popen('tasklist.exe /fo csv',
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)    
    
    return csv.DictReader(p_tasklist.stdout)
    

def listActiveProcesses(image_name):

    process_dict = getProcessDictForImage()
    image_tasklist = []
    
    for p in process_dict:
        if p['Image Name'] == image_name:
            image_tasklist.append(p)
    
    return image_tasklist

def checkForActivePID(pid):
    
    process_dict = getProcessDictForImage()
    
    for p in process_dict:
        if p['PID'] == pid:
            return True
    
    return False

def checkForActivePIDForImage(pid,image_name):
    
    process_dict = getProcessDictForImage()
    
    for p in process_dict:
        if p['PID'] == pid and p['Image Name'] == image_name:
            return True
    
    return False
	
if __name__ == '__main__':
	
    test_pid = '13368'
    test_image = 'chrome.exe'
    wrong_image = 'python.exe'
    
    proc_dict = getProcessDictForImage()
    
    tasklist = listActiveProcesses(test_image)
    
    bl_PID_1000_active = checkForActivePID('1000')
    
    bl_PID_test_active = checkForActivePID(test_pid)
    
    bl_PID_test_wrong_image_active = checkForActivePIDForImage(test_pid,wrong_image)
    
    bl_PID_test_right_image_active = checkForActivePIDForImage(test_pid,test_image)
    
    print(tasklist)
    print('PID 1000 check returns: {}'.format(bl_PID_1000_active))
    print('PID {} check returns: {}'.format(test_pid,bl_PID_test_active))
    print('PID/image {}/{} check returns: {}'.format(test_pid,wrong_image,bl_PID_test_wrong_image_active))
    print('PID/image {}/{} check returns: {}'.format(test_pid,test_image,bl_PID_test_right_image_active))