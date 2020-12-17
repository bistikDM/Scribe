import os
import random
from pathlib import Path


def create_test_storage_environment():
    print("Creating test environment...")
    test_directory = [os.path.join(os.path.abspath(os.sep), "file-picker-dev1", "firmware"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev1", "firmware", "network"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev1", "firmware", "volume"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev2", "firmware"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev2", "firmware", "iso_images"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev3", "configs"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev3", "tools")]
    test_files = ["test_1.1", "test_1.2", "test_1.3",
                  "test_2", "test_3", "test_4",
                  "install", "test", "misc",
                  "duplicate_file", "duplicate_file"]
    for x in test_directory:
        if not Path(x).exists():
            os.makedirs(x)
    for file in test_files:
        random_index = random.randrange(len(test_directory) - 1)
        with open(os.path.join(test_directory[random_index], file), 'wb') as f:
            f.write(os.urandom(16 * 1024 * 1024))  # 16 MB fake files.
            # f.write(os.urandom(128 * 1024)) # 128 KB fake files.
            f.close()
