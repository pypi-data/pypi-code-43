from __future__ import unicode_literals

from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible

import requests, base64, random, time, json


class GitFile(File):

    """
    A file returned from Amazon S3.
    """

    def __init__(self, file, name, storage):
        super(GitFile, self).__init__(file, name)
        self._storage = storage

    def open(self, mode="rb"):
        if self.closed:
            self.file = self._storage.open(self.name, mode).file
        return super(GitFile, self).open(mode)


@deconstructible
class GitStorage(Storage):


    default_auth_settings = {
        "GIT_TOKEN": "",
        "GIT_TOKEN": "",
    }

    """
    An implementation of Django file storage over Github.
    """    
    def __init__(self, option=None):
        token = self.settings.GIT_TOKEN
        url = self.settings.GIT_URL

    '''
    def creat_file(strx=''):
        randx=random.randint(1000, 9999)
        fn= ''+ time.strftime("%Y%m%d%H%M%S", time.localtime())+str(randx)+'.txt'
        with open(fn, 'a+') as f:
            f.write(fn + '\n')
            f.write(strx)
        return fn

    def fn_base64(fn):
        f = open(fn, 'rb')
        fnb64 = base64.b64encode(f.read()).decode('utf-8')
        return fnb64
    '''

    def open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        return self._open(name, mode)

    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)
        return self._save(name, content)

    def put_data(self, token, name, content, url):

        #fn = GitStorage.creat_file('sxs')
        #token = "71d138d77741781535abb4d556dc33d1d92fc93d"
        headers = {"Authorization": 'token '+token}
        #url = "https://api.github.ibm.com/repos/guojial/djangofiles/contents/test.txt"
        url = "https://api.github.ibm.com/repos/guojial/djangofiles/contents/" + name
        print('url' + url)
        d = {"message": "upload content", "committer": {"name": "user", "email": "user@cn.ibm.com"},"content": .content}
        r = requests.put(url = url, data = json.dumps(d), headers = headers)
        rs = r.status_code
        
        if rs == 201:
            print('sucess')
        else:
            print('status==============' + str(rs))

    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace('\\', '/')
 
        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith('/') and not clean_name.endswith('/'):
            # Add a trailing slash as it was stripped.
            return clean_name + '/'
        else:
            return clean_name

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../foo.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
 
        base_path = force_text(self.location)
        base_path = base_path.rstrip('/')
 
        final_path = urljoin(base_path.rstrip('/') + "/", name)
 
        base_path_len = len(base_path)
        if (not final_path.startswith(base_path) or
                final_path[base_path_len:base_path_len + 1] not in ('', '/')):
            raise SuspiciousOperation("Attempted access to '%s' denied." %
                                      name)
        return final_path.lstrip('/')

    def _open(self, name, mode='rb'):
        return File(open(self.path(name), mode))

    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
     
        if hasattr(content, 'chunks'):
            content_str = b''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
     
        self._put_file(name, content_str)
        return cleaned_nam

    def _put_file(self, name, content):
        if self.settings.GIT_TOKEN and self.settings.GIT_URL:
            raise ImproperlyConfigured("Cannot get GIT_TOKEN or GIT_URL.")
        token = self.settings.GIT_TOKEN
        url = self.settings.GIT_URL
        put_data(token, name, content, url)



if __name__ == '__main__':
    
    GitStorage.put_data()
    