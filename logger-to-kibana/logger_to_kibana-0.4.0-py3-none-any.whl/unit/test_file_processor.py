import src.file_processor as processor
from pytest import mark
from unittest.mock import patch


@patch.object(processor.glob, "iglob")
@patch.object(processor, "read_file_for_logs")
@mark.parametrize(
    'folder, returned_files, read_file_count',
    [
        (None, [], 0),
        ("valid", [1, 2], 2),
        ("invalid", [], 0)
    ]
)
def test_process_folder(
        read_file_for_logs, iglob, folder, returned_files, read_file_count):
    iglob.return_value = returned_files
    processor.process_folder(folder)
    assert read_file_for_logs.call_count == read_file_count


@mark.parametrize(
    "file, expected",
    [
        ("setup.py", []),
        ("tests/unit/resources/example.py",
         [
            {"subfolder": "resources",
             "filename": "example.py",
             "function": "lambda_handler",
             "type": "debug",
             "query": 'message: "Initialising"',
             "label": "debug: Initialising"},
            {"subfolder": "resources",
             "filename": "example.py",
             "function": "lambda_handler",
             "type": "info",
             "query": 'message: "Processing"',
             "label": "info: Processing"},
            {"subfolder": "resources",
             "filename": "example.py",
             "function": "lambda_handler",
             "type": "warn",
             "query": 'message: "Success"',
             "label": "warn: Success"},
            {"subfolder": "resources",
             "filename": "example.py",
             "function": "lambda_handler",
             "type": "error",
             "query": 'message: "Failure"',
             "label": "error: Failure"},
            {"subfolder": "resources",
             "filename": "example.py",
             "function": "lambda_handler",
             "type": "critical",
             "query": 'message: "Bananas"',
             "label": "critical: Bananas"},
            {"subfolder": "resources",
             "filename": "example.py",
             "function": "lambda_handler",
             "type": "exception",
             "query": 'message: "Exception"',
             "label": "exception: Exception"},
         ])
    ]
)
def test_read_file_for_logs(file, expected):
    processor.read_file_for_logs(file)
    assert processor.FILE_RESULTS == expected
