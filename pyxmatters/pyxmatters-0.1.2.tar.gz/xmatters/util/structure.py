class Structure(object):

    # Searches the object and returns the associated values in an array
    def searchOnKey(self, keyword, obj):
        arr = []
        for data in obj:
            value = self.doSearch(keyword, data)
            if (value):
                if (obj[data].strip() != ''):
                    arr.append(obj[data])

        return arr

    def doSearch(self, keyword, obj):
        try:
            obj.index(str(keyword))
            value = True
        except:
            value = False
        return value
