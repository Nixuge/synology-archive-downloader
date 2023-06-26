#!/bin/python3
import asyncio
from db_utils import save_all_to_db, save_category_to_db_close
from file_downloader import save_category, save_all_categories
from filelist_parser import download_all
from json_merger import merge_all_categories_v3_v3purged
from random_utils import file_counter

if __name__ == "__main__":
    # asyncio.run(download_all())
    # asyncio.run(save_all_categories())
    
    # asyncio.run(save_category("Os", async_limit=5))

    # asyncio.run(save_category("Package", async_limit=50))

    # asyncio.run(save_category("Utility", async_limit=50))
    # asyncio.run(save_category("Mobile", async_limit=50))
    # asyncio.run(save_category("ChromeApp", async_limit=50))
    # asyncio.run(save_category("ToolChain", async_limit=50))
    # asyncio.run(save_category("Firmware", async_limit=50))

    # print(file_counter("download/ToolChain"))
    # merge_all_categories_v3_v3purged()
    save_all_to_db()
    # save_category_to_db_close("ToolChain")