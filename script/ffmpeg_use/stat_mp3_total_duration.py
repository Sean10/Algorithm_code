#!/bin/python3
import os
import sys
import glob
import json
import logging
import subprocess

def get_file_duration(file):
    process = subprocess.Popen("ffprobe {} -print_format json -show_format -show_streams".format(file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = process.communicate()[0]
    logging.debug(f"stdout: {stdout}")
    format_data = json.loads(stdout)
    duration = parse_duration(file, format_data)
    return duration
    
def parse_duration(file, data):
    format_data = data.get('format', {})
    res = float(format_data.get('duration'))
    if not res:
        res = 0
        logging.error(f"{file} cannot get duration")
    return res

def get_mp3_files(path):
    files = list(glob.glob(os.path.join(path, "*.mp3")))
    return files

def calc_duration(data_list):
    res = sum(data_list)
    return res

def main():
    logging.basicConfig(level=logging.INFO)
    result = []
    files = get_mp3_files(sys.argv[1])
    logging.debug(files)
    for file in files:
        result.append(get_file_duration(file))
    print(calc_duration(result))




main()