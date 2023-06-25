import json
import os
from pprint import pprint
import sqlite3
from sqlite3 import Connection, Cursor
import variables

if not os.path.exists("dbs"):
    os.mkdir("dbs")

PAGES_DB_FILE = "dbs/pages.sqlite3"
PAGES_CONNECTION = sqlite3.connect(PAGES_DB_FILE)
PAGES_CURSOR = PAGES_CONNECTION.cursor()

FILES_DB_FILE = "dbs/files.sqlite3"
FILES_CONNECTION = sqlite3.connect(FILES_DB_FILE)
FILES_CURSOR = FILES_CONNECTION.cursor()

def save_all_to_db():
    for category in variables.CATEGORIES:
          save_category_to_db(category)

def save_category_to_db(category: str):
    print(category)
    with open(f"data/{variables.VERSION}/{category}.json") as of:
        data: dict = json.load(of)
    save_pages_to_db(data)
    save_files_to_db(data)


def save_pages_to_db(category: str, data: dict):
    keys = list(data.keys())
    keys.sort()
    

def save_files_to_db(category: str, data: dict):
    for val in data.values():
        for file in val["files"]:
            # 
            print(file)
    pass

def insert_into_table(table: str):
    return f"""INSERT INTO {table} VALUES (?,?,?,?,?,?);"""

def create_table(table: str):
    return f"""CREATE TABLE IF NOT EXISTS {table} (
            path TEXT NOT NULL,
            md5 CHAR(32),

            lastmodified TEXT,
            platform TEXT,

            websitesize TEXT,
            actualsize INTEGER,

            PRIMARY KEY (path)
            );"""