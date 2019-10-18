from __future__ import absolute_import, division, print_function

import json
import os
import shutil

session_catalog_folder = r'D:\websites\vistoms_interface\sessions_catalog'

for file in os.listdir(session_catalog_folder):
    if os.path.splitext(file)[1] == '.json':
        # Read the file
        session_file_path = os.path.join(session_catalog_folder, file)
        try:
            with open(session_file_path) as f:
                session_details = json.load(f)
        except Exception as e:
            raise SystemError('Could not read the session file {} because of {}.'.format(file, e))
        if 'last_refresh' not in session_details:
            session_folder = session_details['folder']
            try:
                shutil.rmtree(session_folder)
            except Exception as e:
                print("WARNING: Could not remove session folder {}.".format(session_folder))
            os.remove(session_file_path)
            print("Removed session file and session folder for session {}.".format(os.path.basename(file)))
print("Finished cleaning database.")
