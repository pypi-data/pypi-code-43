import sys
import os
import datetime

global app_name
app_name = "eccw"
global app_description
app_description = """
Exact Critical Coulomb Wedge - Graphical User Interface. 
Tools to compute and display the exact solution of any parameter.
"""
global datadir
datadir = os.path.join(get_special_folder_path("CSIDL_APPDATA"), app_name)

def main(argv):
    if "-install" in argv:
        desktop = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
        print("Desktop path: %s" % repr(desktop))
        if not os.path.exists(datadir):
            os.makedirs(datadir)
            dir_created(datadir)
            print("Created data directory: %s" % repr(datadir))
        else:
            print("Data directory already existed at %s" % repr(datadir))

        shortcut = os.path.join(desktop, app_name + ".lnk")
        if os.path.exists(shortcut):
            print("Remove existing shortcut at %s" % repr(shortcut))
            os.unlink(shortcut)

        print("Creating shortcut at %s...\n" % shortcut)
        create_shortcut(
            #r'C:\Python36\python.exe',
            os.path.join(sys.prefix, "pythonw.exe"),
            app_description,
            shortcut, 
            "",
            datadir)
        file_created(shortcut)
        print("Successfull!")
    elif "-remove" in sys.argv:
        print("Removing...")
        pass


if __name__ == "__main__":
    logfile = f"C:\{app_name}_install.log" # Fallback location
    if os.path.exists(datadir):
        logfile = os.path.join(datadir, "install.log")
    elif os.environ.get("TEMP") and os.path.exists(os.environ.get("TEMP"),""):
        logfile = os.path.join(os.environ.get("TEMP"), f"{app_name}_install.log")

    with open(logfile, 'a+') as f:
        f.write("Opened\r\n")
        f.write("Ran %s %s at %s" % (sys.executable, " ".join(sys.argv), datetime.datetime.now().isoformat()))
        sys.stdout = f
        sys.stderr = f
        try:
            main(sys.argv)
        except Exception as e:
            raise
        f.close()

    sys.exit(0)
