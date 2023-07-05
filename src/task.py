import os
import argparse
import shutil
import sys
import threading
import filecmp
from datetime import *


def log_data(log_type, data):
    text = f"[{datetime.now().replace(microsecond=0)}] {log_type}: {data} \n"
    with open(log_file, "a") as file:
        if file.write(text) < 1:
            sys.stderr.write("Cannot write to file")
            sys.exit(2)
    print(text)


def sync():
    threading.Timer(interval, sync).start()
    for path, dirs, files in os.walk(source_folder):
        if path == source_folder:
            path = ""
        else:
            path = "\\".join(path.split("\\")[1:])
        for folder in dirs:
            if not os.path.exists(os.path.join(replica_folder, path, folder)):
                os.mkdir(os.path.join(replica_folder, path, folder))
                log_data("INFO", f'Created folder "{os.path.join(replica_folder, path, folder)}"')
        for filename in files:
            if not os.path.exists(os.path.join(replica_folder, path, filename)):
                shutil.copy2(os.path.join(source_folder, path, filename), os.path.join(replica_folder, path, filename))
                log_data("INFO", f'Created file "{os.path.join(replica_folder, path, filename)}"')
            if not filecmp.cmp(os.path.join(source_folder, path, filename),
                               os.path.join(replica_folder, path, filename)):
                shutil.copy2(os.path.join(source_folder, path, filename), os.path.join(replica_folder, path, filename))
                log_data("INFO", f'Overwrite file "{os.path.join(replica_folder, path, filename)}"')
    for path, dirs, files in os.walk(replica_folder):
        if path == replica_folder:
            path = ""
        else:
            path = "\\".join(path.split("\\")[1:])
        for folder in dirs:
            if not os.path.exists(os.path.join(source_folder, path, folder)):
                clear_folder(os.path.join(replica_folder, path, folder))

        for filename in files:
            if not os.path.exists(os.path.join(source_folder, path, filename)):
                clear_file(os.path.join(replica_folder, path, filename))


def clear_folder(path):
    for del_path, del_dirs, del_files in os.walk(path):
        for file in del_files:
            clear_file(os.path.join(path, file))
        for folder in del_dirs:
            clear_folder(os.path.join(path, folder))
        os.rmdir(path)
        log_data("INFO", f'Deleted folder "{path}"')


def clear_file(path):
    os.remove(path)
    log_data("INFO", f'Deleted file "{path}"')


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--help", action='store_true', help="Show help about interpreter.")
parser.add_argument("--source", help="Source folder to synchronize.")
parser.add_argument("--target", help="Target replica folder.")
parser.add_argument("--log", help="Name of log file")
parser.add_argument("--interval", help="Sync interval (in seconds), default is 300s")
args = parser.parse_args()

if args.help:
    print("""Task for Veeam Software
usage: task.py [--help] [--source=[source_folder]] [--target=[replica_folder]] [--log=[log_file]]
    source          Source folder to synchronize
    target          Target replica folder
    log             Log file
    interval        Sync interval (in seconds), default is 300s""")
    exit(1)
if not (args.source or args.target):
    print("Need to specify source and target folders. Use --help for help")
    exit(1)
if not os.path.exists(args.log):
    with open(args.log, "w") as new_file:
        pass
log_file = args.log
if args.interval:
    interval = int(args.interval)
else:
    interval = 300
if not os.path.exists(args.source):
    os.mkdir(args.source)
source_folder = args.source
if not os.path.exists(args.target):
    os.mkdir(args.target)
replica_folder = args.target
log_data("INFO", "Starting sync script")

sync()
