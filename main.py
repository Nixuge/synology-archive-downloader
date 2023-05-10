import asyncio
from file_downloader import save_all
from filelist_parser import grab_all


categories = ("Os", "Package", "Utility", "Mobile", "ChromeApp", "ToolChain", "Firmware")

if __name__ == "__main__":
    # asyncio.run(grab_all())
    save_all("Os")