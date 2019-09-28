import os
import sys

DAYS = 0
WEEKS = 2

KEEP = (WEEKS * 7) + DAYS

# Get the name of the directory containing this script.
this_dir_path = sys.path[0]
# Get the name of this script.
this_file = os.path.basename(__file__)

# Get all files in the same directory as this script.
backup_files = [ backup_file for backup_file in sorted(os.listdir(this_dir_path), reverse=True) ]
backup_files.remove(this_file)
# Get the absolute paths to all of the backup files.
backup_paths = [ os.path.join(this_dir_path, backup_file) for backup_file in backup_files ]

# Delete backup files older than KEEP days.
if len(backup_paths) > KEEP:
    for backup_path in backup_paths[KEEP:]:
        os.remove(backup_path)
