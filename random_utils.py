import os
import random
import string
import urllib

def random_string(prefix: str = "temp/", letter_count: int = 15) -> str:
    path = prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(letter_count))
    while os.path.exists(path):
        path = prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(letter_count))
    return path


def file_counter(path):
    count = 0
    for file in os.listdir(path):
        file_path = f"{path}/{file}"
        if os.path.isdir(file_path):
            count += file_counter(file_path)
        elif os.path.isfile(file_path):
            count += 1
    return count


def str_to_kb(size_str: str):
    size: float
    if "MB" in size_str:
        size = float(size_str.replace("MB", "").replace(",", "").strip()) * 1_000
    elif "KB" in size_str:
        size = float(size_str.replace("KB", "").replace(",", "").strip())
    elif "GB" in size_str:
        size = float(size_str.replace("GB", "").replace(",", "").strip()) * 1_000_000
    else:
        print("TF?" + size_str)
    return size

def get_file_path_str(url: str):
    url = urllib.parse.unquote(url)
    return url.replace("\n", "").replace("\r", "")

def get_file_path(file_data: dict):
    return get_file_path_str(file_data["url"])
    # fix for LITTERALLY 1 FILE IN PACKAGES THAT HAS \n AND \r IN ITS URL
    # https://global.synologydownload.com/download/Package/spk/DHCPServer/1.0-2281/DHCPServer-x64\r\n-1.0-2281.spk
    # .replace("https://global.synologydownload.com/", "") 
    # for file_value in file_data.values():
    #     if "%" in file_value and not "%20" in file_value and not "%2B" in file_value:
    #         print(file_value)
            # print(urllib.parse.unquote(file_value))
    # for file_key in file_data.keys():
    #     if file_key not in variables.EXISTING_KEYS:
    #         print(file_key)
    #         input()