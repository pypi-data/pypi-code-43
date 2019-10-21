"""
    <!!! WRITE A REALLY GOOD DOCSTRING !!!>
"""
# pylint: disable=W1202,C0111

"""

# ########################################################### #

            Method A - A separate thread for sources.


    * A custom source must follow strict naming convention.
    * A custom source must be named CustomNameExoEdgeSource.
    * A custom source must subclass ExoEdgeSource unless using
      the "classic" 'from module import function' style where
      ExoEdge will just import your installed module and call
      your functions with parameters and positionals.

      E.g.

      # my_module.py

      def my_function(*positionals, **parameters):
          pass

    The rest of the code below can be used as a starting point
    for your custom source.

    A more complete example can be found in:

        github.com/exosite/exoedge_developer_guide
"""

# ########################################################### #

import logging
import sys
import time as _time

from exoedge.sources import ExoEdgeSource
from exoedge_simulator.simulator import *
from exoedge_simulator.sys_info import *
from exoedge_simulator.waves import *

LOG = logging.getLogger(__name__)

class SimulatorExoEdgeSource(ExoEdgeSource):

    def run(self):

        while not self.is_stopped():
            for channel in self.get_channels_by_application("Simulator"):
                if channel.is_sample_time():
                    LOG.warning("sample_time for: {}".format(channel.name))
                    func = channel.protocol_config.app_specific_config['function']
                    if sys.modules.get(__name__) and hasattr(sys.modules[__name__], func):
                        function = getattr(sys.modules[__name__], func)
                        par = channel.protocol_config.app_specific_config['parameters']
                        pos = channel.protocol_config.app_specific_config['positionals']
                        LOG.warning("calling '{}' with: **({})"
                                    .format(function, par))
                        try:
                            channel.put_sample(function(*pos, **par))
                        except Exception as exc: # pylint: disable=W0703
                            LOG.exception("Exception,")
                            channel.put_channel_error(traceback.format_exc())

                    else:
                        channel.put_channel_error(
                            'Simulator has no function: {}'.format(func))

            _time.sleep(0.1)

        LOG.critical("Simulator EXITING!")
