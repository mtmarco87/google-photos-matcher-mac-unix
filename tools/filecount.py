import os
import sys
import json

# Usage: python filecount.py target_folder => counts all the files and folders recursively and returns total count and folder structure

def main():
    target = None

    if len(sys.argv) > 1:
        target = sys.argv[1]

    if target is None or not os.path.exists(target):
        print("Please provide a valid folder")
        return
        
    found_folders = [target]
    total_count = count_files_recursive(target, found_folders)
    
    print("Total files count: " + str(total_count))
    print("Folders structure: " + json.dumps(found_folders))
    

def count_files_recursive(path, found_folders):
    total_count = 0
    if os.path.exists(path):
        contents = os.listdir(path)
        if len(contents) > 0:
            for file in contents:
                if not is_hidden(file):
                    total_count += 1
                    if not os.path.isfile(path + "/" + file):
                        total_count += count_files_recursive(path + "/" + file, found_folders)
                        found_folders.append(path + "/" + file)
                
    return total_count

def is_hidden(file):
    return file.startswith('.')

main()