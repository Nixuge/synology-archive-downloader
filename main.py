import asyncio
from file_downloader import save_category, save_all_categories
from filelist_parser import download_all
from random_utils import file_counter


categories = ("Os", "Package", "Utility", "Mobile", "ChromeApp", "ToolChain", "Firmware")

if __name__ == "__main__":
    # asyncio.run(download_all())
    # asyncio.run(save_all_all_categories())
    asyncio.run(save_category("Package2"))
    # print(file_counter("download/ToolChain"))