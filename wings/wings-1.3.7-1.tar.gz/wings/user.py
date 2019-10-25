import json


class User(object):

    def __init__(self, api_client):
        self.api_client = api_client

    def add_user(self, userid):
        data = {'userid': userid}
        response = self.api_client.session.post(
            self.api_client.get_server() + '/users/common/list/addUser', data)
        if response.text == "OK":
            return True
        return False

    def get_user_details(self, userid):
        response = self.api_client.session.get(
            self.api_client.get_server() + '/users/common/list/getUserJSON?userid=' + userid)
        if response.text:
            return response.json()
        else:
            return None

    def set_user_details(self, userid, password, fullname, isadmin):
        data = {'id': userid, 'fullname': fullname,
                'password': password, 'isAdmin': isadmin}
        postdata = {'userid': userid, 'json': json.dumps(data)}
        self.api_client.session.post(
            self.api_client.get_server() + '/users/common/list/saveUserJSON', postdata)

    def delete_user(self, userid):
        data = {'userid': userid}
        self.api_client.session.post(self.api_client.get_server() + '/users/common/list/removeUser', data)
