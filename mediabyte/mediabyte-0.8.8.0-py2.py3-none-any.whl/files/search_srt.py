#!/home/dd/anaconda3/bin/python
"""Mediabyte .vtt keyword search module"""
import re, os
from datetime import datetime
from . import cnf
from . import dl2

def time_in_seconds(time_str):
    """Takes time code string, returns integer time in seconds"""
    hours = int(time_str[:2])
    minutes = int(time_str[3:5])
    seconds = int(time_str[6:])
    seconds_total = hours * 3600 + minutes * 60 + seconds
    return seconds_total

def combine(time_list, min_clip_length):
    """Takes list of time codes, combines intervals shorter than min_clip_length"""
    new_list = [time_list[0]]
    comparison = new_list[-1]
    for i in range(1, len(time_list)):
        difference_in_secs = time_in_seconds(time_list[i]) - time_in_seconds(comparison)
        if difference_in_secs >= min_clip_length:
            new_list.append(time_list[i])
        comparison = time_list[i]
    return new_list

def get_filename(yt_hash):
    """Takes YouTube hash, returns subtitle file name match"""
    files = os.listdir('/home/dd/anaconda3/lib/python3.7/site-packages/mediabyte/srt/')
    filename = ""
    for filename_str in files:
        if yt_hash in filename_str:
            filename = filename_str        
    if filename == "":
        #raise ValueError("File not found")
        return dl2.dl_srt(yt_hash)
    
    full_filename = cnf.srt_folder_path + cnf.os_sep + filename
    return full_filename

def parse_subtitles(search_term, content, min_clip_length):
    """Takes subtitle file content, search_term and min_clip_length, returns list of time code strings"""
    result_list = []
    for i, line in enumerate(content):
        m = re.findall(search_term, line)
        if m:
            time_match = re.search(r"\d\d:\d\d:\d\d\.\d\d\d", line)
            prev_match = re.search(r"\d\d:\d\d:\d\d\.\d\d\d", content[i-1])
            # use the in-line time code if found
            if time_match:
                result_list.append(time_match.group(0)[:-4])
            # or use time code from previous line
            elif prev_match:
                result_list.append(prev_match.group(0)[:-4])

    sorted_list = sorted(set(result_list))
    if len(sorted_list) > 1:
        final_list = combine(sorted_list, min_clip_length)
    elif len(sorted_list) == 1:
        final_list = sorted_list
    else:
        final_list = []
    return final_list

def time_code_to_yt_time(time_str):
    hours = int(time_str[:2])
    minutes = int(time_str[3:5])
    seconds = int(time_str[6:])
    result_str = ""
    if hours:
        result_str += str(hours) + "h"
    if minutes:
        result_str += str(minutes) + "m"
    if seconds:
        result_str += str(seconds) + "s"
    return result_str

def build_youtube_url(yt_hash, time_code):
    url = "https://youtu.be/" + yt_hash

    full_url = url + "?t=" + str(time_in_seconds(time_code))
    return full_url

def main(search_term, yt_hash, min_clip_length=10):
    """Takes search term and YouTube hash, returns list of time codes of occurrences"""

    filename = get_filename(yt_hash)
    with open(filename, 'r') as f:
        content = f.readlines()
    result = parse_subtitles(search_term, content, min_clip_length)
    yt_urls = []
    for item in result:
        yt_urls.append(build_youtube_url(yt_hash, item))

    return yt_urls
