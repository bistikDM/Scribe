import os
import random
from pathlib import Path


def create_test_storage_environment():
    print("Creating test environment...")
    test_directory = [os.path.join(os.path.abspath(os.sep), "Scribe-dev1", "firmware"),
                      os.path.join(os.path.abspath(os.sep), "Scribe-dev1", "firmware", "network"),
                      os.path.join(os.path.abspath(os.sep), "Scribe-dev1", "firmware", "volume"),
                      os.path.join(os.path.abspath(os.sep), "Scribe-dev2", "firmware"),
                      os.path.join(os.path.abspath(os.sep), "Scribe-dev2", "firmware", "ISO_images"),
                      os.path.join(os.path.abspath(os.sep), "Scribe-dev3", "configs"),
                      os.path.join(os.path.abspath(os.sep), "Scribe-dev3", "tools")]
    test_files = ["test_1_1.txt", "test_1_2.txt", "test_1_3.txt",
                  "test_2.txt", "test_3.txt", "test_4.txt",
                  "install.txt", "test.txt", "misc.txt",
                  "duplicate_file.txt", "duplicate_file.jpeg"]
    for x in test_directory:
        if not Path(x).exists():
            os.makedirs(x)
    for file in test_files:
        random_index = random.randrange(len(test_directory))
        with open(os.path.join(test_directory[random_index], file), 'wb') as f:
            f.write(os.urandom(16 * 1024 * 1024))  # 16 MB fake files.
            # f.write(os.urandom(128 * 1024)) # 128 KB fake files.
            f.close()
