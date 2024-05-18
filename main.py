import os
import sys,ctypes
import stat
import wmi
c = wmi.WMI()
#count sector
# ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def disk_count():
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
if is_admin():
    disk_count()
else:
    # if sys.version_info[0] == 3:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    # else:
        #ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(" ".join(sys.argv)), None, 1)
    disk_count()
#pause the screen
os.system("pause")