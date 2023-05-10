from asyncio import Task
import asyncio
import hashlib
import json
import os
import shutil
from typing import Callable

import urllib

import httpx

from random_utils import random_string

categories = ("Os", "Package", "Utility", "Mobile", "ChromeApp", "ToolChain", "Firmware")

existing_keys = ("url", "Last modified", "Size", "Platform", "MD5")

def get_file_path(file_data: dict):
    return (urllib.parse.unquote(file_data["url"]))
    # .replace("https://global.synologydownload.com/", "") 
    # for file_value in file_data.values():
    #     if "%" in file_value and not "%20" in file_value and not "%2B" in file_value:
    #         print(file_value)
            # print(urllib.parse.unquote(file_value))
    # for file_key in file_data.keys():
    #     if file_key not in existing_keys:
    #         print(file_key)
    #         input()



def get_grabbed_urls(json_file) -> dict:
    with open(json_file, "r") as file:
        data = json.load(file)
    return data

async def save_category(json_file) -> list:
    downloader = Downloader()
    data = get_grabbed_urls("data/v3/" + json_file + ".json")
    for url_data in data.values():
        files = url_data["files"]
        for file in files:
            downloader.remaining_elements.append(get_file_path(file))

    await downloader.download_all()

async def save_all_categories() -> dict:
    for category in categories:
        await save_category(category)


class AsyncLimiter:
    tasks: list[Task]
    remaining_elements: list
    done_tasks_count: int
    print_progress_str: str
    polling_sleep: float
    max_task_count: int
    function_for_task: Callable # str bc idc how to put a function there lmao

    def __init__(self,
                 function_to_task, #Function to call
                 print_progress_str: str = "Downloaded/Remaining tasks: {downloaded!s}/{remaining!s}, Running tasks: {running_tasks!s} ({failed_tasks!s} failed)     ",
                 max_task_count: int = 20,
                 polling_sleep: float = .2
                 ) -> None:
        self.done_tasks_count = 0
        self.failed_tasks_count = 0
        self.remaining_elements = []
        self.tasks = []
        self.print_progress_str = print_progress_str
        self.function_for_task = function_to_task
        self.max_task_count = max_task_count
        self.polling_sleep = polling_sleep

    # To be called & returned when an error occurs
    # eg:
    # try:
    #     ....
    # except:
    #     return fail(elem)
    #
    # Will automatically add back to the remaining list & return false
    def fail(self, element):
        self.done_tasks_count -= 1
        self.failed_tasks_count += 1
        self.remaining_elements.append(element)
        return False

    async def download_all(self):
        while True:    
            for element in self.remaining_elements:
                if (len(self.tasks) > self.max_task_count):
                    break
                self.tasks.append(asyncio.create_task(self.function_for_task(element)))
                self.remaining_elements.remove(element)

            for task in self.tasks:
                if task.done():
                    self.tasks.remove(task)
                    self.done_tasks_count += 1

            print(self.print_progress_str.format(
                downloaded=self.done_tasks_count,
                remaining=len(self.remaining_elements),
                running_tasks=len(self.tasks),
                failed_tasks=self.failed_tasks_count
            ), end="\r")

            if len(self.tasks) == 0:
                break

            await asyncio.sleep(self.polling_sleep)
        
        print("\n== Done with batch ==")


class Downloader(AsyncLimiter):
    def __init__(self) -> None:
        super().__init__(self.download_file, max_task_count=30, polling_sleep=.05)
    
    async def download_file(self, url: str):
        final_path = url.replace("https://global.synologydownload.com/", "")
        final_folder = os.path.dirname(final_path)

        if os.path.isfile(final_path):
            return
        
        if not os.path.isdir(final_folder):
            os.makedirs(final_folder)

        # return

        client = httpx.AsyncClient()

        # ===== Downloading the actual file =====
        try:
            r = await client.get(url)
        except:
            return self.fail(url)
        
        temp_filename = random_string()
        # md5 = hashlib.md5()
        with open(temp_filename, 'wb') as f:
            for chunk in r.iter_bytes(chunk_size=4096):
                # md5.update(chunk)
                f.write(chunk)

        # ===== other checks, metadata things & moving the file =====
        # md5 = md5.hexdigest()
        
        shutil.move(temp_filename, final_path)

        return True