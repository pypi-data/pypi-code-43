import os


class Domain(object):

    def __init__(self, api_client):
        self.api_client = api_client

    def import_domain(self, url):
        data = {'domain': os.path.basename(url), 'location': url}
        self.api_client.session.post(self.api_client.get_server() + '/users/' +
                                     self.api_client.get_username() + '/domains/importDomain', data)

    def get_domain_details(self, domain):
        response = self.api_client.session.get(
            self.api_client.get_server() + '/users/' +
            self.api_client.get_username() + '/domains/getDomainDetails?domain=' + domain
        )
        if response.text:
            return response.json()
        else:
            return None

    def select_default_domain(self, domain):
        data = {'domain': domain}
        self.api_client.session.post(self.api_client.get_server() + '/users/' +
                                     self.api_client.get_username() + '/domains/selectDomain', data)

    def delete_domain(self, domain):
        data = {'domain': domain}
        self.api_client.session.post(self.api_client.get_server() + '/users/' +
                                     self.api_client.get_username() + '/domains/deleteDomain', data)
