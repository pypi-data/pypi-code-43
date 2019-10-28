
from .apivideo_request import BaseRequest


class Video(BaseRequest):
    def list_all_videos(self):
        return self.api_get('/videos', need_auth=True)

    def get_video(self, videoId):
        return self.api_get('/videos/{videoId}'.format(videoId=videoId), need_auth=True)

    def create_video(self, video_title='Unknown', description='', tags=[], **kwargs):
        body = {
            'title': video_title,
            'description': description,
            'tags': tags
        }
        body.update(**kwargs)
        return self.api_post('/videos', body=body, need_auth=True)

    def upload_video(self, video_id, file):
        return self.api_post('/videos/{id}/source'.format(id=video_id), files=file, need_auth=True)

    def patch_video(self, video_id, **kwargs):
        return self.api_patch('/videos/{id}'.format(id=video_id), body=kwargs, need_auth=True)

    def delete_video(self, video_id):
        return self.api_delete('/videos/{id}'.format(id=video_id), need_auth=True)

    def post_token(self):
        return self.api_post('/tokens', need_auth=True)
