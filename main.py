from __future__ import annotations # return type of current class

import asyncio
from dataclasses import dataclass
import json
from typing import Callable
from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx
from asyncio import Task

@dataclass
class File:
    path: str
    date: str
    size: str

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "date": self.date,
            "size": self.size
        }

    @staticmethod
    def from_dict(data: dict) -> File:
        return File(
            path=data.get("path"),
            date=data.get("date"),
            size=data.get("size")
        )
    

def get_grabbed_urls() -> dict:
    with open("data.json", "r") as file:
        data = json.load(file)
    return data


files: list[File] = []
BASE_URL = "https://archive.synology.com"
EPIC_STRING = "Downloaded/Remaining tasks: {downloaded!s}/{remaining!s}, Running tasks: {running_tasks!s} (failed:{failed!s}, skipped:{skipped!s})    "

class DATA:
    total_failed = 0
    skipped = 0
    json_lock = False

POLLING_SLEEP = .2


async def set_grabbed_urls(url: str, files: list[File], inner_urls: list[str]):
    while DATA.json_lock == True:
        await asyncio.sleep(.01)
        await set_grabbed_urls(url, files, inner_urls)
    DATA.json_lock = True

    current_data = get_grabbed_urls()
    if url in current_data.keys():
        DATA.json_lock = False
        return

    current_data[url] = {
        "files": [file.to_dict() for file in files],
        "inner_urls": inner_urls
    }

    with open("data.json", "w") as file:
        json.dump(current_data, file, indent=4)
    DATA.json_lock = False


class PageGrabber:
    async def get_page(self, url: str) -> list[Callable]:
        full_url = url if "http" in url else BASE_URL + url

        grabbed_keys = get_grabbed_urls()
        if full_url in grabbed_keys.keys():
            DATA.skipped += 1
            url_dict = grabbed_keys[full_url]

            for inner_file in url_dict["files"]:
                files.append(File.from_dict(inner_file))
            
            return [self.get_page(inner_url) for inner_url in url_dict["inner_urls"]]
    
        try:
            r = await httpx.AsyncClient().get(full_url)
        except Exception as e:
            # print(f"exception ! {e} for url {url}")
            DATA.total_failed += 1
            await asyncio.sleep(3)
            return await self.get_page(url)


        soup = BeautifulSoup(r.text, "lxml")
        body: Tag = soup.find("tbody")
        try:
            rows: list[Tag] = body.find_all("tr")
        except:
            print(f"Error ! {body} {url}")
            DATA.total_failed += 1
            await asyncio.sleep(3)
            return await self.get_page(url)
        
        current_subfolders: list[str] = []
        current_files: list[File] = []

        for row in rows:
            th = row.find("th")
            if not th: continue

            href = th.find("a").get("href")
            svg = th.find("svg")

            if "bi-folder" in svg.get("class"):
                current_subfolders.append(href)
                # print("Added folder " + href)
            else:
                tds: list[Tag] = row.find_all("td")
                date = tds[0].text
                size = tds[1].text
                file = File(href, date, size)
                current_files.append(file)
        
        await set_grabbed_urls(full_url, current_files, current_subfolders)
    
        for file in current_files:
            files.append(current_files)
        
        return [self.get_page(folder) for folder in current_subfolders]


async def wait_all_tasks(to_call: list[Callable]) -> list[Callable]:
    tasks: list[Task] = []
    callable_to_return: list[Callable] = []
    max_task_count = 30
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
            skipped=DATA.skipped
        ), end="\r")

        await asyncio.sleep(POLLING_SLEEP)
        
    print("\n== Done with batch ==")
    return callable_to_return

async def grab_everything(callable: list[Callable]):
    result = await wait_all_tasks(callable)
    if len(result) > 0:
        await grab_everything(result)

async def main():
    pg = PageGrabber()
    tasks = await pg.get_page("/download/Os")
    await grab_everything(tasks)
 

async def test_ip():
    print((await httpx.AsyncClient().get("https://api.ipify.org/")).text)

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(test_ip())
