"""
The file_processor is in charge of processing the files
looking for the log_mappings to generate an object with
the function, log_message and level
"""

import re
import glob
from pathlib import Path
from src.configuration import config

FILE_RESULTS = []

LOG_MAPPING = [
    {
        "type": "debug",
        "detector": config.file_parsers.LogDebugDetector,
        "filter": config.file_parsers.LogDebugFilter,
    },
    {
        "type": "info",
        "detector": config.file_parsers.LogInfoDetector,
        "filter": config.file_parsers.LogInfoFilter,
    },
    {
        "type": "warn",
        "detector": config.file_parsers.LogWarnDetector,
        "filter": config.file_parsers.LogWarnFilter,
    },
    {
        "type": "error",
        "detector": config.file_parsers.LogErrorDetector,
        "filter": config.file_parsers.LogErrorFilter,
    },
    {
        "type": "critical",
        "detector": config.file_parsers.LogCriticalDetector,
        "filter": config.file_parsers.LogCriticalFilter,
    },
    {
        "type": "exception",
        "detector": config.file_parsers.LogExceptionDetector,
        "filter": config.file_parsers.LogExceptionFilter,
    },
]


def process_folder(folder: str) -> []:
    if not folder:
        folder = ""
    for file in glob.iglob(folder + config.file_parsers.FilesMatchFilter,
                           recursive=True):
        read_file_for_logs(file)
    return FILE_RESULTS


def read_file_for_logs(filename: str):
    with open(filename) as f:
        function = ""
        for line in f:
            if re.findall(config.file_parsers.FunctionMappingDetector, line):
                function = re.findall(
                            config.file_parsers.FunctionMappingFilter,
                            line)[0]
            else:
                process_line_log_mapping(line, function, filename)


def process_line_log_mapping(line: str, function, filename):
    for mapping in LOG_MAPPING:
        if re.findall(mapping["detector"], line):
            message = re.findall(mapping["filter"], line)
            if message:
                FILE_RESULTS.append({
                    "subfolder": get_folder_name(filename),
                    "filename": get_file_name(filename),
                    "function": function,
                    "type": mapping["type"],
                    "query": 'message: "' + message[0] + '"',
                    "label": mapping["type"] + ": " + message[0]
                })
                return


def get_folder_name(folder: str) -> str:
    return Path(folder).parts[-2]


def get_file_name(folder: str) -> str:
    return Path(folder).parts[-1]
