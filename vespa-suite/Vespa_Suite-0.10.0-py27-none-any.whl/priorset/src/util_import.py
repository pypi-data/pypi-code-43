# Python modules
from __future__ import division

# 3rd party modules


# Our modules



from vespa.common.util.import_ import Importer

import mrs_priorset


class PriorsetImporter(Importer):
    def __init__(self, source):
        Importer.__init__(self, source, None, False)

    def go(self, add_history_comment=False):
        for element in self.root.getiterator("priorset"):
            self.found_count += 1

            priorset = mrs_priorset.Priorset(element)
            
            self.imported.append(priorset)

        self.post_import()
        
        return self.imported
