import os
import time

folder_path = '/path/to/your/log/files'
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    # Check the time of the last access time and the current time
    if os.path.getmtime(file_path) < time.time() - 30 * 86400:
        os.remove(file_path)
