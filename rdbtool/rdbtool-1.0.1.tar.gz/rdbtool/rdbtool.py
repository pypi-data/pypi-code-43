# %%
import dropbox
import time

class RDB:
    def __init__(self, token, project):
        self.DB_TOKEN = token
        self.dbx = dropbox.Dropbox(self.DB_TOKEN)
        self.dbx.users_get_current_account()
        self.project = project
        self.lock = False
    
    def download_file(self, file_name, db_file, lock=False):
        '''
        ファイルのダウンロード
        [i] file_name:ファイル名, db_file:ダウンロード元のファイル, lock:ロックを取得
        '''
        if lock:
            while True:
                if not self.lock:
                    self.lock = True
                    self.dbx.files_download_to_file(file_name, '/{}/{}'.format(self.project, db_file))
                    return
                else:
                    time.sleep(1)
        else:
            self.dbx.files_download_to_file(file_name, '/{}/{}'.format(self.project, db_file))
    
    def upload_file(self, file_name, db_file, overwrite=False):
        '''
        ファイルのアップロード
        [i] file_name:ファイル名, db_file:アップロード先のファイル名, overwrite:上書き
        '''
        if overwrite:
            mode = dropbox.files.WriteMode.overwrite
        else:
            mode = dropbox.files.WriteMode.add

        with open(file_name , "rb" ) as f:
            self.dbx.files_upload(f.read(), '/{}/{}'.format(self.project, db_file), mode=mode)

        self.lock = False
    
    def get_shared_link(self, db_file):
        '''
        共有リンクの取得
        [i] db_file:DBのファイル名
        [o] link:共有リンク
        '''
        links = self.dbx.sharing_list_shared_links(path='/{}/{}'.format(self.project, db_file), direct_only=True).links

        if links is not None:
            for link_t in links:
                link = link_t.url.strip('?dl=0')
                link = link.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
                
                return link

        return self._create_shared_link(db_file)

    def _create_shared_link(self, db_file):
        '''
        リンクの作成
        [i] db_file:DBのファイル名
        [o] link:共有リンク
        '''
        setting = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
        link_t = self.dbx.sharing_create_shared_link_with_settings(path='/{}/{}'.format(self.project, db_file), settings=setting)

        link = link_t.url.strip('?dl=0')
        link = link.replace('www.dropbox.com', 'dl.dropboxusercontent.com')

        return link
