import json
import os
from pprint import pprint
import sqlite3
from sqlite3 import Connection, Cursor
import variables
import random_utils
import hashlib

DB_FOLDER = "/home/nix/dbs"

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

PAGES_DB_FILE = f"{DB_FOLDER}/pages.sqlite3"
PAGES_CONNECTION = sqlite3.connect(PAGES_DB_FILE)
PAGES_CURSOR = PAGES_CONNECTION.cursor()

FILES_DB_FILE = f"{DB_FOLDER}/files.sqlite3"
FILES_CONNECTION = sqlite3.connect(FILES_DB_FILE)
FILES_CURSOR = FILES_CONNECTION.cursor()

def save_all_to_db():
    for category in variables.CATEGORIES:
        save_category_to_db(category)
    FILES_CONNECTION.close()

def save_category_to_db_close(category: str):
    save_category_to_db(category)
    FILES_CONNECTION.close()

def save_category_to_db(category: str):
    print("\nSaving category: " + category)
    with open(f"data/{variables.VERSION_FULL}/{category}.json") as of:
        data: dict = json.load(of)
    save_pages_to_db(category, data)
    # save_files_to_db(category, data)
    FILES_CONNECTION.commit()
    FILES_CONNECTION.serialize()
    PAGES_CONNECTION.commit()
    PAGES_CONNECTION.serialize()


def save_pages_to_db(category: str, data: dict):
    PAGES_CURSOR.execute(PageQueries.create_file_table(category))

    keys = list(data.keys())
    keys.sort()
    
    for path in keys:
        if PAGES_CURSOR.execute(PageQueries.is_page_into_table(category, path)).fetchone():
            print("|", end="")
            continue
    
        current_data = data[path]

        files = current_data["files"]
        files = [file["url"].replace("https://global.synologydownload.com", "") for file in files]
        if len(files) == 0 or files == "":
            files = None
        else:
            files = json.dumps(files)
            
        inner_urls = current_data["inner_urls"]
        if len(inner_urls) == 0 or inner_urls == "":
            inner_urls = None
        else:
            inner_urls = json.dumps(inner_urls)
        
        PAGES_CURSOR.execute(
            PageQueries.insert_page_into_table(category),
            (path, files, inner_urls)
        )
    

def save_files_to_db(category: str, data: dict):
    FILES_CURSOR.execute(FileQueries.create_file_table(category))
    ll = len(data.values())

    keys = list(data.keys())
    keys.sort()

    for index, key in enumerate(keys):
        val = data[key]
        print(f"\n{index+1} / {ll} ({key})", end=" ")
        for file in val["files"]:
            path = random_utils.get_file_path(file).replace("https://global.synologydownload.com/", "")
            if FILES_CURSOR.execute(FileQueries.is_file_into_table(category, path)).fetchone():
                print("|", end="")
                continue
            websitemd5 = file.get("MD5")
            md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
            lastmodified = file.get("Last modified")
            platform = file.get("Platform")

            websitesize = file.get("Size")
            actualsize = os.stat(path).st_size

            FILES_CURSOR.execute(
                FileQueries.insert_file_into_table(category),
                (path, websitemd5, md5, lastmodified, platform, websitesize, actualsize)
            )
        FILES_CONNECTION.commit()
        FILES_CONNECTION.serialize()
            # print(file)
    pass

def get_where_contains_key(table: str, column: str, value: str):
    return f"""SELECT * FROM {table} WHERE {column}=\"{value}\""""

class PageQueries:
    @staticmethod
    def is_page_into_table(table: str, filepath: str):
        return get_where_contains_key(table, "path", filepath)

    @staticmethod
    def insert_page_into_table(table: str):
        return f"""INSERT INTO {table} VALUES (?,?,?);"""

    @staticmethod
    def create_file_table(table: str):
        return f"""CREATE TABLE IF NOT EXISTS {table} (
                path TEXT NOT NULL,

                files TEXT,
                innerurls TEXT,

                PRIMARY KEY (path)
                );"""

class FileQueries:
    @staticmethod
    def is_file_into_table(table: str, filepath: str):
        return get_where_contains_key(table, "path", filepath)
    
    @staticmethod
    def insert_file_into_table(table: str):
        return f"""INSERT INTO {table} VALUES (?,?,?,?,?,?,?);"""

    @staticmethod
    def create_file_table(table: str):
        return f"""CREATE TABLE IF NOT EXISTS {table} (
                path TEXT NOT NULL,

                websitemd5 CHAR(32),
                md5 CHAR(32),

                lastmodified TEXT,
                platform TEXT,

                websitesize TEXT,
                actualsize INTEGER,

                PRIMARY KEY (path)
                );"""