from __future__ import annotations # return type of current class

import asyncio
from dataclasses import dataclass
import json
import os
import time
from typing import Callable
from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx
from asyncio import Task
import variables
import random_utils

# @dataclass
# class File:
#     path: str
#     date: str
#     size: str

#     def to_dict(self) -> dict:
#         return {
#             "path": self.path,
#             "date": self.date,
#             "size": self.size
#         }

#     @staticmethod
#     def from_dict(data: dict) -> File:
#         return File(
#             path=data.get("path"),
#             date=data.get("date"),
#             size=data.get("size")
#         )
    

failed_urls: list[str] = []
files: list[dict] = []
BASE_URL = "https://archive.synology.com"
EPIC_STRING = "Downloaded/Remaining tasks: {downloaded!s}/{remaining!s}, Running tasks: {running_tasks!s} (success: {success!s}|fail:{failed!s}|skip:{skipped!s})    "
FILE_VERSION = variables.VERSION
POLLING_SLEEP = .2


class DATA:
    successful_noskip = 0
    total_failed = 0
    skipped = 0
    json_lock = False
    json_file = ""


def get_grabbed_urls(bypass_lock=False) -> dict:
    try:
        while not bypass_lock and DATA.json_lock == True:
            time.sleep(.01)
        
        if not bypass_lock: DATA.json_lock = True
        with open(DATA.json_file, "r") as file:
            data = json.load(file)

        if not bypass_lock: DATA.json_lock = False
        return data
    except:
        if not bypass_lock: DATA.json_lock = False
        print("exception! (may or may not be normal)")
        return None

async def set_grabbed_urls(url: str, files: list[dict], inner_urls: list[str]):
    while DATA.json_lock == True:
        await asyncio.sleep(.01)
    DATA.json_lock = True

    current_data = get_grabbed_urls(bypass_lock=True)
    if url in current_data.keys():
        DATA.json_lock = False
        return

    current_data[url] = {
        "files": files,
        "inner_urls": inner_urls
    }

    with open(DATA.json_file, "w") as file:
        json.dump(current_data, file, indent=4)
        
    DATA.json_lock = False


class PageGrabber:
    def get_tags(self, header: Tag):
        tr = header.find("tr")
        fields: list[Tag] = tr.find_all("th", {"scope": "col"})
        # print()
        fields_list: list[str] = [field.text for field in fields]
        fields_list.pop(0)
        return fields_list

    async def handleException(self, url: str, message: str = "") -> list[Callable]:
        print(message)
        DATA.total_failed += 1

        # temp debug handling
        # failed_urls.append(url)
        # return []

        # permanent normal handling
        await asyncio.sleep(3)
        return await self.get_page(url)

    async def get_page(self, url: str) -> list[Callable]:
        full_url = url if "http" in url else BASE_URL + url
        grabbed_keys = get_grabbed_urls()
        if url in grabbed_keys.keys():
            DATA.skipped += 1
            url_dict = grabbed_keys[url]

            for inner_file in url_dict["files"]:
                files.append(inner_file)
            return [self.get_page(inner_url) for inner_url in url_dict["inner_urls"]]
    
        try:
            r = await httpx.AsyncClient().get(full_url, timeout=15)
        except Exception as e:
            return await self.handleException(url, f"exception! {type(e)} for url {url}")

        if r.status_code != 200:
            print(full_url)
            return await self.handleException(url, f"Non-200 status code! {url} ({r.status_code})")


        soup = BeautifulSoup(r.text, "lxml")
        body: Tag = soup.find("tbody")
        header: Tag = soup.find("thead")
        try:
            rows: list[Tag] = body.find_all("tr")
            tags: list[str] = self.get_tags(header)
        except:
            return await self.handleException(url, f"Error ! {body} {url}")
        
        current_subfolders: list[str] = []
        current_files: list[dict] = []

        for row in rows:
            th = row.find("th")
            if not th: continue

            href = th.find("a").get("href").replace("https://archive.synology.com", "")
            svg = th.find("svg")

            if "bi-folder" in svg.get("class"):
                current_subfolders.append(href)
                # print("Added folder " + href)
            else:
                tds: list[Tag] = row.find_all("td")

                file = {"url": href}
                for index, tag in enumerate(tags):
                    file[tag] = tds[index].text

                current_files.append(file)
        
        await set_grabbed_urls(url, current_files, current_subfolders)
    
        for file in current_files:
            files.append(current_files)
        
        return [self.get_page(folder) for folder in current_subfolders]


async def wait_all_tasks(to_call: list[Callable]) -> list[Callable]:
    DATA.skipped = 0
    DATA.successful_noskip = 0
    tasks: list[Task] = []
    callable_to_return: list[Callable] = []
    max_task_count = 20
    done_tasks_count = 0
    while True:
        for element in to_call:
            if (len(tasks) > max_task_count):
                break
            tasks.append(asyncio.create_task(element))
            to_call.remove(element)

            
        for task in tasks:
            if task.done():
                for result in task.result():
                    callable_to_return.append(result)
                
                tasks.remove(task)
                done_tasks_count += 1
            
        if len(tasks) == 0:
            break
    
        print(EPIC_STRING.format(
            downloaded=done_tasks_count,
            remaining=len(to_call),
            running_tasks=len(tasks),
            # failed=0
            failed=DATA.total_failed,
            skipped=DATA.skipped,
            success=DATA.successful_noskip
        ), end="\r")

        await asyncio.sleep(POLLING_SLEEP)
        
    print("\n== Done with batch ==")
    return callable_to_return

async def grab_everything(callable: list[Callable]):
    result = await wait_all_tasks(callable)
    if len(result) > 0:
        await grab_everything(result)

async def getTaskSetJson(path):
    print(f"======= Grabbing category {path} =======")
    DATA.json_file = f"data/{FILE_VERSION}/{path}.json"

    if not get_grabbed_urls():
        if not os.path.exists(f"data/{FILE_VERSION}/"):
            os.makedirs(f"data/{FILE_VERSION}/")
        with open(DATA.json_file, "w") as file:
            file.write("{}")

    pg = PageGrabber()
    tasks = await pg.get_page(f"/download/{path}") 
    
    await grab_everything(tasks)
    print(f"======= Done with category {path} =======")

async def download_all():
    await getTaskSetJson("Os")
    await getTaskSetJson("Firmware")
    await getTaskSetJson("ToolChain")
    await getTaskSetJson("Utility")
    await getTaskSetJson("Mobile")
    await getTaskSetJson("ChromeApp")
    await getTaskSetJson("Package")
    for cat in ["Os", "Package", "Utility", "Mobile", "ChromeApp", "ToolChain", "Firmware"]:
        count_size(cat)
    

def count_size(path: str):
    DATA.json_file = f"data/{FILE_VERSION}/{path}.json"

    file_count = 0
    file_no_size = 0
    total_filesize_kb = 0
    urls_dict: dict = get_grabbed_urls()
    for key, val in urls_dict.items():
        file_count += 1
        for file in val["files"]:
            size = file.get("Size")
            if not size:
                file_no_size += 1
                continue
            total_filesize_kb += random_utils.str_to_kb(size)
    print(f"===== CATEGORY: {path} =====")
    print(f"Filecount: {file_count} ({file_no_size} without a size)")
    print(f"Total files size: {int(total_filesize_kb/1_000)}MB ({int(total_filesize_kb/1_000_000)}GB)")
    print()


async def test_ip():
    print((await httpx.AsyncClient().get("https://api.ipify.org/")).text)

# if __name__ == "__main__":
    # asyncio.run(main())

    # for file in failed_urls:
    #     print("https://archive.synology.com" + file)
    # print(len(failed_urls))

    # asyncio.run(test_ip())
