# Imports
from __future__ import absolute_import, division, print_function

import logging
import kadmos.vistoms.vistoms as vistoms_interface


# Settings for the logger
logger = logging.getLogger(__name__)
# logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename='interface.log', level=logging.INFO)

# Settings for the interface
app = vistoms_interface.interface(debug=False)

if __name__ == '__main__':
    # Run the interface
    app.run(threaded=True)
