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
    print("Saving category: " + category)
    with open(f"data/{variables.VERSION_FULL}/{category}.json") as of:
        data: dict = json.load(of)
    # save_pages_to_db(category, data)
    save_files_to_db(category, data)
    FILES_CONNECTION.commit()
    FILES_CONNECTION.serialize()


def save_pages_to_db(category: str, data: dict):
    keys = list(data.keys())
    keys.sort()
    

def save_files_to_db(category: str, data: dict):
    FILES_CURSOR.execute(create_file_table_query(category))
    ll = len(data.values())

    keys = list(data.keys())
    keys.sort()

    for index, key in enumerate(keys):
        val = data[key]
        print(f"\n{index+1} / {ll} ({key})", end=" ")
        for file in val["files"]:
            path = random_utils.get_file_path(file).replace("https://global.synologydownload.com/", "")
            if FILES_CURSOR.execute(is_file_into_table_query(category, path)).fetchone():
                print("|", end="")
                continue
            websitemd5 = file.get("MD5")
            md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
            lastmodified = file.get("Last modified")
            platform = file.get("Platform")

            websitesize = file.get("Size")
            actualsize = os.stat(path).st_size

            FILES_CURSOR.execute(
                insert_file_into_table_query(category),
                (path, websitemd5, md5, lastmodified, platform, websitesize, actualsize)
            )
        FILES_CONNECTION.commit()
        FILES_CONNECTION.serialize()
            # print(file)
    pass

def get_where_contains_key(table: str, column: str, value: str):
    return f"""SELECT * FROM {table} WHERE {column}=\"{value}\""""

def is_file_into_table_query(table: str, filepath: str):
    return get_where_contains_key(table, "path", filepath)

def insert_file_into_table_query(table: str):
    return f"""INSERT INTO {table} VALUES (?,?,?,?,?,?,?);"""

def create_file_table_query(table: str):
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