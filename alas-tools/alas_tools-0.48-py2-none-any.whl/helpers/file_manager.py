class CachedFileManager(object):
    wsdl_cache = {}

    @classmethod
    def get(cls, file_path, file_content_callback=None):
        if file_path not in cls.wsdl_cache:
            with open(file_path, 'r') as f:
                file_content = f.read()

                if file_content_callback:
                    file_content = file_content_callback(file_content)

                cls.wsdl_cache.update({file_path: file_content})
        return cls.wsdl_cache[file_path]
