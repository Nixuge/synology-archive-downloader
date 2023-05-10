import asyncio
from file_downloader import save_category, save_all_categories
from filelist_parser import download_all


categories = ("Os", "Package", "Utility", "Mobile", "ChromeApp", "ToolChain", "Firmware")

if __name__ == "__main__":
    # asyncio.run(grab_all())
    # asyncio.run(save_all_all_categories())
    asyncio.run(save_category("ChromeApp"))