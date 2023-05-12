import os
import random
import string

def random_string(prefix: str = "temp/", letter_count: int = 15) -> str:
    path = prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(letter_count))
    while os.path.exists(path):
        path = prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(letter_count))
    return path

def file_counter(path):
    count = 0
    for file in os.listdir(path):
        file_path = f"{path}/{file}"
        if os.path.isdir(file_path):
            count += file_counter(file_path)
        elif os.path.isfile(file_path):
            count += 1
    return count
    