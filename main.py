import os
import sys,ctypes
import wmi
c = wmi.WMI()
#Check if the script is running as admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
#Count the size of disk in the system
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
            print(diskDriver.Name, "have", disk_size, "bytes")
            print("BytesPerSector:", diskDriver.BytesPerSector)
            print("Total Sectors:", disk_size // diskDriver.BytesPerSector)
        return diskDriver
#Execute the script as admin 
def read_sector(disk, sector_no = 0):
    with open(disk.Name, "rb", buffering=0) as f:
        f.seek(sector_no * disk.BytesPerSector)
        read = f.read(disk.BytesPerSector)
        for i in range(0, len(read), 16):
            print(" ".join("{:02x}".format(c) for c in read[i:i+16]))
def write_sector(disk, sector_no, data):
    with open(disk.Name, "r+b", buffering=0) as f:
        f.seek(sector_no * disk.BytesPerSector)
        f.write(data)
#Main function
def main():
    if is_admin():
        pass
    else:
    # if sys.version_info[0] == 3:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    # else:
        #ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(" ".join(sys.argv)), None, 1)
    diskDrive = disk_count()
    read_sector(diskDrive, 0)
    # write_sector(diskDrive, 0, b"Hello World")
if __name__ == "__main__":
    main()
#pause the screen
os.system("pause")