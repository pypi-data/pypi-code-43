import linecache
from list_based_flavorpack.processing_classes.third_party_processing import rules

class ThirdPartyProcessingClass:
    '''
    An example of a processing  class for a list based pool/region.
    Returns UUIDs stored in memory.
    '''
    def __init__(self):
        '''
        Sets processing rules.
        '''
        self.pre_processing_rules = [rules.ValidNumberDirectory, rules.SufficientNumbersStorage]
        self.post_processing_rules = []
    
    def get_pre_processing_rules(self):
        '''
        Returns processing rules to be executed prior to the generator running.
        '''
        return self.pre_processing_rules
    
    def get_post_processing_rules(self):
        '''
        Returns processing rules to be executed after the generator has run.
        '''
        return self.post_processing_rules

    def get_items(self, region, size):
        '''
        Pull numbers from the file created/updated from rules previously executed.
        '''
        first = region.last_number_line
        max_line = first + size
        lines = []
        linecache.checkcache(filename=region.file_path)
        for lineno in range(first, max_line):
            item = linecache.getline(region.file_path, lineno).strip()
            if not item:
                raise ValueError("There are not enough numbers available for this iteration starting on line number: %s", lineno)
            lines.append(item)
        region.last_number_line = max_line
        region.save()
        return lines
