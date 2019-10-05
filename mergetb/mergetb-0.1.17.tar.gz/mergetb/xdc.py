from subprocess import call
import mergetb.lib as mergelib

def web(pid, eid, name):
    """Open up your web browser to the XDC Jupyter interface

    :param pid: project id
    :param eid: experiment id
    :param name: xdc name
    """

    token = mergelib.xdc_token(pid, eid, name)
    call([
        "xdg-open",
        "https://xdc.mergetb.io/%s/%s/%s/?token=%s"%(pid, eid, name, token)
    ])
