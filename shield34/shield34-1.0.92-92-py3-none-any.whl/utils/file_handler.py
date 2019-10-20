import os, fnmatch

import requests


from shield34_reporter.model.enums.file_type import FileType

def upload_file(run_contract_id, block_run_contract_id, file_name_to_save, file):
    from shield34_reporter.model.contracts.s3_file_details import S3FileDetails
    from shield34_reporter.utils.aws_utils import AwsUtils
    screen_shot_details_contract = S3FileDetails(run_contract_id, block_run_contract_id,
                                                 file_name_to_save, FileType.SCREEN_SHOT.value)
    pre_signed_url_contract = AwsUtils.get_file_upload_to_s3_url(screen_shot_details_contract)
    http_response = requests.put(pre_signed_url_contract.url, data=file)
    if http_response.status_code == 200:
        return True

class FileHandler:

    @staticmethod
    def find_files(directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    return filename

        return ""
