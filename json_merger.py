import json
import os
import variables

# A pretty dirty script
# that's made to merge the purged json & the normal one
# to get both the old & new files into a single json

def merge_all_categories_v3_v3purged():
    bp1 = "data/v3"
    bp2 = "data/v3-purged"
    sp = "data/v3-purged-normal-merge"
    if not os.path.exists(sp):
        os.makedirs(sp)
    for category in variables.CATEGORIES:
        merge_jsons(f"{bp1}/{category}.json", f"{bp2}/{category}.json", f"{sp}/{category}.json")


def merge_jsons(json1: str, json2: str, output_path: str):
    with open(json1, 'r') as of1:
        data1: dict = json.load(of1)
    with open(json2, 'r') as of2:
        data2: dict = json.load(of2)
    
    keys1 = data1.keys()
    keys2 = data2.keys()

    # Merge whole entries
    for key in keys2:
        if key not in keys1:
            data1[key] = data2[key]


    for key, val in data1.items():
        if key in keys2:
            compare_complete_inner_list(val, data2[key], "files")
            compare_complete_inner_list(val, data2[key], "inner_urls")

    with open(output_path, "w") as of:
        json.dump(data1, of, indent=4)

def compare_complete_inner_list(val1: dict, val2: dict, key: str):
    if not val1[key] == val2[key]:
        for elem in val2[key]:
            if elem in val1[key]: 
                continue
            else:
                val1[key].append(elem)
    