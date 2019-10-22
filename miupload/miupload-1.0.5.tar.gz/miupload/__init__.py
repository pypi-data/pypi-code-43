"""
This module provides verification of user's email and password.


"""

import miupload.runningConfiguration as cfg
import requests
import time

name = "miupload"
log = ""

# Check if module is configured and ready.
try:
    if (cfg.configured):
        ready = True
    else:
        ready = False
except:
    ready = False

try:
    if (cfg.base_url):
        base_url = cfg.base_url
    else:
        base_url = "http://sss-data.minerva.community"
except:
    base_url = "http://sss-data.minerva.community"

def get_status():
    """
    For DEBUG. Returns login status and server base_url.
    :return:
    """
    global ready
    global base_url
    print(ready,base_url)
    return ready


def login(token):
    """

    Function checks access token and then saves configuration data for later use.

    :param email:
    :param token:
    :return:
    """
    global ready
    global base_url
    if (ready):
        Q = input("Module is already configured. Rewrite? (y/n): ")
        if (Q == "y"):
            pass
        else:
            "Answer is not y. Configuration aborted."
            return None

    print("Contacting data server...")

    r = requests.post(base_url+"/User/validate_v2", data={'psw': token})
    res = str(r.content, 'utf-8', 'ignore')
    if (res == "FALSE"):
        print("Verification failed! Please check your Minerva email and password. Try again!")
        return False
    elif (res.split(";")[0] == 'TRUE'):  # TODO
        print("Verification successful! Saving Configuration "+res.split(";")[1]+"...")
        cfg.email = res.split(";")[1]
        cfg.psw = token
        cfg.configured = True
        ready = True
    else:
        print("Verification failed! Please check your Minerva email and password. Try again!")
        return False

    print("MiUpload configuration saved successfully!")

def login_gui():
    """
    Ask user to login with prompt for email and password.

    :return:
    """
    return login(input("Enter your unique access token: "))


def set_server(new_url):
    """
    For DEBUG only. Allows to change server address and redirect communication to alternative server.

    :param url:
    :return:
    """
    global base_url

    cfg.base_url = new_url
    base_url = new_url
    return True


def submit_notebook(assignment = None):
    """

    :param assignment:
    :return:
    """
    global ready
    global base_url
    global log
    if (not ready):
        print("You are not logged in!")
        print("Please run miupload.login_gui()")
        return False

    try:
        from IPython.display import display, Javascript, HTML

        display(HTML("""<br><div class="progress">
          <div id="dynamic" class="progress-bar progress-bar-info progress-bar-striped active" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">
            <span id="current-progress"></span>
          </div>
        </div>"""))
    except ImportError:
        print("Autosaving failed. Please make sure to save your notebook before submitting notebook.")
    else:
        print("Autosaving notebook...")  # save notebook before reading of file


    def progress_bar_step(name, step=10):
        try:
            display(Javascript("""
                var current_progress = parseInt($("#dynamic").attr("aria-valuenow"));
                  current_progress += """+str(step)+""";  
                  $("#"""+name+"""")
                  .css("width", current_progress + "%")
                  .attr("aria-valuenow", current_progress)
                  .text(current_progress + "% Complete");
                  """))
            return True
        except:
            return False
    progress_bar_step("dynamic",step=5)

    display(Javascript("IPython.notebook.save_notebook()"),
                   include=['application/javascript'])
    display(Javascript("""$(function() {
          var interval3 = setInterval(function() {
               var current_progress = parseInt($("#dynamic").attr("aria-valuenow"));
              current_progress += 1;
              $("#dynamic")
              .css("width", current_progress + "%")
              .attr("aria-valuenow", current_progress)
              .text(current_progress + "% Complete");
              if (current_progress >= 30)
                  clearInterval(interval3);
          }, 200);
        });"""))
    time.sleep(5)

    print("Notebook saved.")
    print("Preparing .ipynb upload")
    # Get filename of notebook for uploading
    # Source: https://github.com/jupyter/notebook/issues/1000
    import json
    import os.path
    import re
    import ipykernel
    import requests

    # try:  # Python 3
    #    from urllib.parse import urljoin
    # except ImportError:  # Python 2
    #    from urlparse import urljoin

    # Alternative that works for both Python 2 and 3:
    from requests.compat import urljoin

    try:  # Python 3 (see Edit2 below for why this may not work in Python 2)
        from notebook.notebookapp import list_running_servers
    except ImportError:  # Python 2
        import warnings
        from IPython.utils.shimmodule import ShimWarning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ShimWarning)
            from IPython.html.notebookapp import list_running_servers

    def get_notebook_name():
        global log
        """
        Return the full path of the jupyter notebook.
        """
        kernel_id = re.search('kernel-(.*).json',
                              ipykernel.connect.get_connection_file()).group(1)
        servers = list_running_servers()
        log += "[DEBUG] Getting Server List\n"
        log += "[DEBUG] Servers:" + repr(servers) + "\n"
        for ss in servers:
            log += "[DEBUG] URL:" + urljoin(ss['url'], 'api/sessions')+ "\n"
            log += "[DEBUG] Params:" + str(repr(ss.get('token', '')))+"\n"
            response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                    params={'token': ss.get('token', '')})
            log += "[DEBUG] Response:" + response.text +"\n"
            for nn in json.loads(response.text):
                try:
                    log += "[DEBUG] Kernel:" + str(repr(nn)) + "\n"
                    if nn['kernel']['id'] == kernel_id:
                        relative_path = nn['notebook']['path']
                        return os.path.join(ss['notebook_dir'], relative_path)
                except:
                    log += "[DEBUG] Failed to get kernel:" + repr( nn) + "\n"

                    display(HTML("""<div class="alert alert-block alert-warning">
                    <b>Failed to get filename of notebook from API!</b> <br>---> Please copy and paste filename and path of notebook <b>from URL</b> (copy everything after .../notebooks/
                    </div>"""))
                    relative_path = input("path/filename.ipynb: ")
                    return os.path.join(ss['notebook_dir'], relative_path)

    display(Javascript("""$(function() {
             var interval4 = setInterval(function() {
                  var current_progress = parseInt($("#dynamic").attr("aria-valuenow"));
                 current_progress += 1;
                 $("#dynamic")
                 .css("width", current_progress + "%")
                 .attr("aria-valuenow", current_progress)
                 .text(current_progress + "% Complete");
                 if (current_progress >= 55)
                     clearInterval(interval4);
             }, 30);
           });"""))
    display(Javascript("""$(function() {
      var interval = setInterval(function() {
           var current_progress = parseInt($("#dynamic").attr("aria-valuenow"));
          current_progress += 1;
          $("#dynamic")
          .css("width", current_progress + "%")
          .attr("aria-valuenow", current_progress)
          .text(current_progress + "% Complete");
          if (current_progress >= 91)
              clearInterval(interval);
      }, 600);
    });"""))
    filename = get_notebook_name()
    files = {'upload_file': open(filename, 'rb')}
    values = {'email': cfg.email, 'assignment': assignment , "debug": log}
    try:
        r = requests.post(base_url+"/Notebook/submit", files=files, data=values)
        if (str(r.content, 'utf-8', 'ignore')[0] == "Y"):

            display(HTML("""<div class="alert alert-block alert-success">
    <b>Upload successful!</b> You can view your submitted notebook on """ +'<a target="_blank" href="https://nbviewer.jupyter.org/urls/'+base_url.replace("https://","").replace("http://","")+"/uploads/"+str(r.content, 'utf-8', 'ignore')[1:]+'"'+""" class="alert-link"> nbviewer.</a>
    </div>"""))
            display(Javascript("""
                    $(function() {
                  var interval2 = setInterval(function() {
                    var current_progress = parseInt($("#dynamic").attr("aria-valuenow"));
                      current_progress += 1;
                      $("#dynamic")
                      .css("width", current_progress + "%")
                      .attr("aria-valuenow", current_progress)
                      .text(current_progress + "% Complete");
                      if (current_progress >= 100)
                      $("#dynamic").addClass('progress-bar-success')
                      .removeClass('progress-bar-info')
                      .removeClass('active')
                      if (current_progress >= 100)
                          clearInterval(interval2);  
                  }, 60);
                });"""))

            return True
        else:
            display(HTML("""<div class="alert alert-block alert-danger">
                                <b>Upload failed!</b> Error:"""+ str(r.content, 'utf-8', 'ignore')+ """  <br>Please email your notebook to your peer tutor manually.
                                </div>"""))
            display(Javascript("""
                              $("#dynamic")
                              .addClass('progress-bar-danger')
                              .removeClass('progress-bar-info')
                              .removeClass('active')
                          """))
            return False
    except ConnectionError:
        display(HTML("""<div class="alert alert-block alert-danger">
                                        <b>Upload failed!</b> Error: Cannot connect with the server. <br>Please check your internet connection. If the problem persist, email your notebook to your peer tutor manually.
                                        </div>"""))
        display(Javascript("""
                                      $("#dynamic")
                                      .addClass('progress-bar-danger')
                                      .removeClass('progress-bar-info')
                                      .removeClass('active')
                                  """))
        return False
    except:
        display(HTML("""<div class="alert alert-block alert-danger">
                                                <b>Upload failed!</b> Error: Cannot connect with the server...<br>Please check your internet connection. If the problem persist, email your notebook to your peer tutor manually.
                                                </div>"""))
        display(Javascript("""
                                              $("#dynamic")
                                              .addClass('progress-bar-danger')
                                              .removeClass('progress-bar-info')
                                              .removeClass('active')
                                          """))
        return False


def nbgrader_download(assignment, token = None, group = None, filename=None, folder=None):
    import os
    import requests
    import json
    if (filename == None):
        filename = assignment
    if (folder == None):
        folder = assignment

    if (token!=None):
        pass
    else:
        token= cfg.psw
    print("Contacting data server")
    try:
        if group == None:
            r = requests.get(base_url + "/Notebook/download_list/" + str(token) + "/" + str(assignment))
        else:
            r = requests.get(base_url + "/Notebook/download_list/" + str(token) + "/" + str(assignment) + "/" + str(group))
    except:
        print("Failed to connect with the server, please check your internet connection")
        return False
    print ("Parsing received data")
    try:
        data= json.loads(r.content)
    except:
        print ("Failed to parse received data")
        print ("RAW DATA:", data)
        return False
    print("Found ",len(data), "submitted notebooks.")
    print("Preparing required folder structure")

    # create submitted folder
    if not os.path.exists(os.getcwd()+"/submitted"):
        os.makedirs(os.getcwd()+"/submitted")
    for row in data:
        # create user folder
        if not os.path.exists(os.getcwd() + "/submitted/"+row["u_name"].replace(" ","_")):
            os.makedirs(os.getcwd() + "/submitted/"+row["u_name"].replace(" ","_"))
        # create assignment folder
        if not os.path.exists(os.getcwd() + "/submitted/"+row["u_name"].replace(" ","_")+"/"+folder):
            os.makedirs(os.getcwd() + "/submitted/"+row["u_name"].replace(" ","_")+"/"+folder)

        # download file
        url = base_url + "/uploads/" + row["s_filename"]
        r = requests.get(url, allow_redirects=True)
        open(os.getcwd() + "/submitted/"+row["u_name"].replace(" ","_")+"/"+folder+"/"+filename+".ipynb", 'wb').write(r.content)

        print("Assignment saved successfully")

    print("Notebook are ready to be graded")

