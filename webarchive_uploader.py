import asyncio
import json
import os
from pprint import pprint
import threading
import time
from internetarchive import get_item, get_files
from requests.models import Response
from file_downloader import AsyncLimiter
import random_utils

#CACHE_FILE
CF = "cache/webarchive_packages.cache"

def add_to_cache(path: str):
    with open(CF, "a") as of:
        of.write(path + "\n")

def is_in_cache(path: str) -> bool:
    if not os.path.exists(CF):
        open(CF, "w").write("")
    
    with open(CF, "r") as of:
        for line in of.readlines():
            if line.replace("\n", "") == path:
                return True
    
    return False

def upload_path(path: str):
    if is_in_cache(path):
        # print("Already in cache: " + path)
        return False
    # print("Uploading: " + path)

    md = {'collection': 'Software', 'title': 'archive.synology.com (pre purge)', 'mediatype': 'software'}
    item = get_item(CURRENT_ID)
    responses: list[Response] = item.upload(files=[path], metadata=md, verbose=False)

    # filepath = '/'.join(r.url.split('/')[4:])

    all_good = True
    for r in responses:
        if r.status_code != 200:
            print("SOME ERROR!!!")
            all_good = False
    
    if all_good:
        add_to_cache(path)

    return True

    # print(r[0].status_code)


def check_pathes_valid(path_list: list[str]):
    archive_pathes = [f.name for f in get_files(CURRENT_ID)]
    for path in path_list:
        if path not in archive_pathes:
            print("MISSING FILE: " + path)
    # print(archive_pathes)


class FolderFinder:
    def __init__(self, base_folder: str, starting_letter_range: str, ending_letter_range: str) -> None:
        self.base_folder = base_folder

        self.check_len = len(starting_letter_range)
        if self.check_len != len(ending_letter_range):
            raise Exception("Starting range & ending range must have the same letter count.")
        self.slr = starting_letter_range.lower()
        self.elr = ending_letter_range.lower()

        self.dirs = self._sort_list(os.listdir(base_folder))

    def _sort_list(self, old_list: str) -> list:
        # sort() is case sensitive while linux isn't
        lower_list = [elem.lower() for elem in old_list]
        lower_list.sort()

        # so we using lowered list to sort & a dict to get back the normal caps
        lower_normal_dict = {}
        for key in old_list:
            i = lower_list.index(key.lower())
            lower_normal_dict[lower_list[i]] = key

        return [lower_normal_dict[x] for x in lower_list]

    def _check_high_limit(self, name_start: str) -> bool:
        for i in range(self.check_len):
            if i == 0: continue # skip 1st iter as already done in main loop
            h_limit = ord(self.elr[i])
            current_char = ord(name_start[i])
            if current_char > h_limit:
                return False
            elif current_char < h_limit:
                return True
        return True

    def _check_low_limit(self, name_start: str) -> bool:
        for i in range(self.check_len):
            if i == 0: continue # skip 1st iter as already done in main loop
            l_limit = ord(self.slr[i])
            current_char = ord(name_start[i])
            if current_char < l_limit:
                return False
            elif current_char > l_limit:
                return True
        return True

    def _is_in_range(self, dir: str) -> bool:
        name_start = dir[:self.check_len].lower()

        l_limit = ord(self.slr[0])
        h_limit = ord(self.elr[0])
        first_char = ord(name_start[0])

        # (always valid, eg "b" between "a" and "c")
        if l_limit < first_char and first_char < h_limit:
            return True
                
        # (eg "a" between "a" and "c")
        elif l_limit == first_char:
            return self._check_low_limit(name_start)

        # (eg "c" between "a" and "c")
        elif h_limit == first_char:
            return self._check_high_limit(name_start)

        return False

    def find(self) -> list[str]:
        valid_dirs = []
        for dir in self.dirs:
            if self._is_in_range(dir):
                valid_dirs.append(dir)

        return valid_dirs


class ArchiveUploader:
    def __init__(self, thread_count: int = 1) -> None:
        self.thread_count = thread_count
        self.threads: list[threading.Thread] = []

    def clean_threads(self):
        for thread in self.threads:
            if not thread.is_alive():
                self.threads.remove(thread)
    
    def save(self, path: str):
        t = threading.Thread(target=upload_path, args=(path,))
        t.start()
        self.threads.append(t)
    
    def save_all(self, path_list: list[str]):
        while len(path_list) > 0:
            print(f"\r[ArchiveUploader] running: {len(self.threads)}, remaining: {len(path_list)}     |", end="")
            if len(self.threads) < self.thread_count:
                self.save(path_list[0])
                path_list.pop(0)
            
            self.clean_threads()

            time.sleep(.1)
    

async def main():
    pkg1 = FolderFinder("download/Package/spk", "aaa", "hyb").find()
    
    pkg2 = FolderFinder("download/Package/spk", "hyperb", "python").find()
    pkg2.remove("Python2")
    pkg2.remove("Python3.9")
    pkg2.remove("PythonModule")

    pkg3 = FolderFinder("download/Package/spk", "python", "zarafa").find()
    pkg3.remove("Python")

    pkg_fixed = [f"download/Package/spk/{folder}" for folder in pkg1]
    uploader = ArchiveUploader()
    uploader.save_all(pkg_fixed)

    # check_pathes_valid(None)

    # upload_path(full_path)

PKG1 = 'archive.synology.com_packages_aaa-hyb'
PKG2 = 'archive.synology.com_packages_hyp-python'
# PKG3 = 'archive.synology.com_packages_aaa-hyb'

CURRENT_ID = PKG1

if __name__ == "__main__":
    asyncio.run(main())
    # upload_path('download/Package/spk/AcronisTrueImage')