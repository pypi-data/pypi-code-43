import json
import requests
from shield34_reporter.consts.shield34_properties import Shield34Properties
from shield34_reporter.model.contracts.pre_signed_url_contract import PreSignedUrlContract


class AwsUtils():

    @staticmethod
    def get_file_upload_to_s3_url(s3_file_details):
        from shield34_reporter.auth.sdk_authentication import SdkAuthentication
        payload = json.dumps(s3_file_details.__dict__)
        headers = {'content-type': 'application/json',
                   'Authorization': 'Shield34-Project ' + SdkAuthentication.get_user_token()}
        request = requests.post(Shield34Properties.api_base_url + '/report/get-presigned-upload-url', data=payload, headers=headers, verify=True)
        if request.status_code == 200:
            content_as_json = request.json()
            pre_signed_url = PreSignedUrlContract(content_as_json['data']['url'], content_as_json['data']['timestamp'], content_as_json['data']['fileName'])
            return pre_signed_url
        return ""
