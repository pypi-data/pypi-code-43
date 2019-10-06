import random
import string

def FindDictKeyByValueIndex(target: dict, value):
    return list(target.keys())[list(target.values()).index(value)]

class UniqueIDMap:
    occasion_keys = {}
    occasion_values = {}

    def __init__(self, *args, **kwargs):
        pass
        
    def summon_uniqueid(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=72))

    def __setitem__(self, key, value):
        uniqueid = self.summon_uniqueid()
        self.occasion_keys[uniqueid] = key
        self.occasion_values[uniqueid] = value

    def __getitem__(self, key):
        uniqueid = FindDictKeyByValueIndex(self.occasion_keys, key)
        return self.occasion_values[uniqueid]

    def get(self, key):
        try:
            uniqueid = FindDictKeyByValueIndex(self.occasion_keys, key)
            return self.occasion_values[uniqueid]
        except ValueError:
            return None

if __name__ == "__main__":
    p = UniqueIDMap()
    p[{'faq': "faq"}] = {"faq": 2}
    print(p[{"faq": "faq"}])
    print(p.get('nothing'))