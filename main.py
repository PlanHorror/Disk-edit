import os
import sys
import stat
import wmi
c = wmi.WMI()
#count sector
for diskDriver in c.query("Select * FROM Win32_DiskDrive"):
    
    disk_size = int(diskDriver.size)
    sector_size = diskDriver.BytesPerSector
    with open(diskDriver.Name, "rb", buffering=0) as f:
        f.seek(disk_size)
        while True:
            try:
                f.read(sector_size)
                disk_size += sector_size
            except PermissionError:
                break
        print(diskDriver.Name, "have", disk_size,)
#pause the screen
os.system("pause")