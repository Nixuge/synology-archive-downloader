import os
import random
import string

def random_string(prefix: str = "temp/", letter_count: int = 15) -> str:
    path = prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(letter_count))
    while os.path.exists(path):
        path = prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(letter_count))
    return path