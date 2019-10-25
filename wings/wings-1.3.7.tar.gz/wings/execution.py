import json


class Execution(object):

    def __init__(self, api_client):
        self.api_client = api_client

    def list_executions_by_page(self, page=0, pattern=None, status=None, limit=1000):
        start = limit*page
        params = {"start": start, "limit": limit}
        if pattern:
            params['pattern'] = pattern
        if status:
            params['status'] = status

        resp = self.api_client.session.get(self.api_client.get_request_url() + 'executions/getRunListSimple',
                                           params=params)
        return self.api_client.check_request(resp)

    def get_run_details(self, execution_id):
        postdata = {'run_id': execution_id}
        resp = self.api_client.session.post(self.api_client.get_request_url() + 'executions/getRunDetails',
                                            data=postdata)
        return self.api_client.check_request(resp)

    def delete_run(self, execution_id):
        json_data = json.dumps({"id": execution_id})
        postdata = {'json': json_data}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        resp = self.api_client.session.post(self.api_client.get_request_url() + 'executions/deleteRun',
                                            data=postdata,
                                            headers=headers)
        return self.api_client.check_request(resp)

    def publish(self, execution_id):
        postdata = {'run_id': execution_id}
        resp = self.api_client.session.post(self.api_client.get_request_url() + 'executions/publishRun', data=postdata)
        return self.api_client.check_request(resp)
