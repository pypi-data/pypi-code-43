import ConfigParser
import os

mainPath=os.path.dirname(os.path.abspath( __file__ ))
config = ConfigParser.RawConfigParser()
if os.path.exists(os.path.expanduser("~/.pcp.cfg")):
	config.read(os.path.expanduser("~/.pcp.cfg"))
else: config.read("/etc/pcp.cfg")


grab_files=config.get('FILES','grab_files').split(",")
rsync_options=config.get('FILES','rsync_options')

