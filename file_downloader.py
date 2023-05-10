import json


known_keys = ("")

def get_file_path(file_data: dict):
    print(file_data)
    input()


def get_grabbed_urls(json_file) -> dict:
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

def save_all(json_file) -> dict:
    data = get_grabbed_urls("data/v3/" + json_file + ".json")
    for url in data.keys():
        print(url)