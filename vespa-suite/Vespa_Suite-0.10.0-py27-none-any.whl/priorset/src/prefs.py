# Python modules
from __future__ import division
import abc

# 3rd party modules

# Our modules
import util_menu
import util_priorset_config
import vespa.common.prefs as prefs

"""See common/prefs.py for info on the classes below."""

class PriorsetPrefs(prefs.Prefs):
    __metaclass__ = abc.ABCMeta
    def __init__(self, id_class):
        prefs.Prefs.__init__(self, util_menu.bar, id_class)

    @property
    def _ConfigClass(self):
        """Returns the appropriate ConfigObj class for this app."""
        return util_priorset_config.Config


class PrefsMain(PriorsetPrefs):
    def __init__(self):
        PriorsetPrefs.__init__(self, util_menu.ViewIds)


    @property
    def _ini_section_name(self):
        return "main_prefs"


    def deflate(self):
        # Call my base class deflate
        d = PriorsetPrefs.deflate(self)

        # Add my custom stuff
        for name in ("sash_position",
                     "line_color_baseline",
                     "line_color_imaginary", 
                     "line_color_magnitude",
                     "line_color_metabolite", 
                     "line_color_real", 
                     "zero_line_color", 
                     "zero_line_style", 
                     "line_width", 
                    ):
            d[name] = getattr(self, name)

        return d


    def inflate(self, source):
        # Call my base class inflate
        PriorsetPrefs.inflate(self, source)

        # Add my custom stuff
        for name in ("sash_position", ):
            setattr(self, name, int(source[name]))

        for name in ("line_color_baseline",
                     "line_color_imaginary", 
                     "line_color_magnitude",
                     "line_color_metabolite", 
                     "line_color_real", 
                     "zero_line_color", 
                     "zero_line_style",
                    ):
            setattr(self, name, source[name])

        for name in ("line_width", ):
            setattr(self, name, float(source[name]))


