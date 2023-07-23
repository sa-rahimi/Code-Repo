import os
import glob
import shutil

in_dir = r"Type Address to Your Files"
Out_dir = r"ype Address Where You Want to Move Your Files to"

search_criteria = '*.txt'
query = os.path.join(in_dir, search_criteria)
file_paths = glob.glob(query)
file_paths.sort()

keyword = "Type Your Keyword"

target_files = []
for file in file_paths:
    with open(file) as f:
        line = f.read()
        if keyword in line:
            target_files.append(file)
        f.close

for target in target_files:
    shutil.move(target, Out_dir)
