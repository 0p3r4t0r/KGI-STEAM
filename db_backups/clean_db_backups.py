import os


DAYS = 0
WEEKS = 2

KEEP = (WEEKS * 7) + DAYS

backups = sorted(os.listdir(), reverse=True)
backups.remove(__file__)
if len(backups) > KEEP:
    for backup in backups[KEEP:]:
        print(backup)
