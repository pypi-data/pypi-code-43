import sys

import slack


def upload_file(file_path):
    client = slack.WebClient(
        token='xoxp-784267530339-797604595559-796057345621-79b8eea77260e3a2c0627ad161745840'
    )
    response = client.files_upload(
        channels='#backend',
        file=file_path,
        title='Pytest report',
        initial_comment='Summary of failed test cases',
        filename='pytest_report',
    )
    assert response["ok"]


if __name__ == '__main__':
    path = sys.argv[1]
    print('uploading file {} to slack'.format(path))
    upload_file(path)
