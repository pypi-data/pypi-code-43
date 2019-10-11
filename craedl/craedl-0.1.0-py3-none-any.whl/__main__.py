# Copyright 2019 The Johns Hopkins University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import getpass
import os
import stat
import sys

def main():
    """
    The ``craedl-token`` console script entry point for configuring the Craedl
    authentication token.
    """
    if sys.platform == 'win32':
        token_path = os.path.abspath(os.path.join(os.sep, 'Users',
            os.getlogin(), 'AppData', 'Local', 'Craedl', 'craedl'))
    elif sys.platform == 'darwin':
        token_path = os.path.abspath(os.path.join(os.sep, 'Users',
            os.getlogin(), 'Library', 'Preferences', 'Craedl', 'craedl'))
    else:
        token_path = os.path.expanduser('~/.config/Craedl/craedl')
    argv = sys.argv

    if len(argv) > 1:
        sys.exit('craedl-token configures your Craedl authentication token, which you can obtain\nfrom your Craedl account. Visit https://craedl.org/docs#api-access for more information.')

    else:
        token = getpass.getpass('Enter your token: ')

        if len(token) != 40:
            sys.exit('The provided token is invalid.')

        if not os.path.exists(os.path.dirname(token_path)):
            os.makedirs(os.path.dirname(token_path))
            
        f = open(token_path, 'w+')
        f.write(token)
        f.close()

        os.chmod(token_path, stat.S_IREAD | stat.S_IWRITE)

if __name__ == "__main__":
    main()
