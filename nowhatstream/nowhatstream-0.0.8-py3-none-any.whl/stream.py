
from .apivideo_request import BaseRequest


class Stream(BaseRequest):
    def list_all_live(self):
        ret = self.api_get('/live-streams', need_auth=True)
        return ret

    def get_livestream(self, id):
        return self.api_get('/live-streams/{id}'.format(id=id), need_auth=True)

    def create_livestream(self, stream_name='Unknown', player_id=0):
        body = {
            'name': stream_name,
            'player_id': player_id
        }
        return self.api_post('/live-streams', body=body, need_auth=True)

    def delete_livestream(self, livestream_id):
        return self.api_delete('/live-streams/{id}'.format(id=livestream_id), need_auth=True)

    def patch_livestream(self, livestream_id, **kwargs):
        return self.api_patch('/live-streams/{id}'.format(id=livestream_id), body=kwargs, need_auth=True)

    def upload_thumbnail(self, livestream_id, thumbnail):
        return self.api_post('/live-streams/{id}/thumbnail'.format(id=livestream_id), files=thumbnail, need_auth=True)

    def delete_thumbnail(self, livestream_id):
        return self.api_delete('/live-streams/{id}/thumbnail'.format(id=livestream_id), need_auth=True)
