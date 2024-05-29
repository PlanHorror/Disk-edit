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
            print("Total Sectors:", disk_size // diskDriver.BytesPerSector)
        return diskDriver
#Execute the script as admin 
def read_sector(disk, sector_no):
    with open(disk.Name, "rb", buffering=0) as f:
        f.seek(sector_no * disk.BytesPerSector)
        read = f.read(disk.BytesPerSector)
        print("Sector", sector_no)
        print("Offset:", f.tell() - disk.BytesPerSector)    
    #Show bit in sector with ASCII and Hex
        for i in range(0, len(read), 16):
            print(" ".join("{:02x}".format(c) for c in read[i:i+16]), end=" ")
            print("".join(chr(c) if 32 <= c <= 126 else "." for c in read[i:i+16]))
def write_sector(disk, sector_no, data):
    with open(disk.Name, "r+b", buffering=0) as f:
        f.seek(sector_no * disk.BytesPerSector)
        f.write(data)
def read_sector_in_volume(volume_name, sector_no):
    disk_fd = os.open(volume_name, os.O_RDONLY | os.O_BINARY)
    data = os.read(disk_fd, (sector_no + 1) * 512) 
    #format data in hex with 16 hex in a row
    print("Volume", volume_name.split("\\")[-1])
    print("Sector", sector_no)
    print("Offset:", sector_no * 512)

    for i in range(0, len(data)):
        if i % 16 == 0:
            if i != 0:
                for j in range(i-16, i):
                    print(chr(data[j]) if 32 <= data[j] <= 126 else ".", end="")
            print()
        #print hex and ascii
        print("{:02x}".format(data[i]), end=" ")
        if i == len(data) - 1:
            for j in range(i - 15, i+1):
                print(chr(data[j]) if 32 <= data[j] <= 126 else ".", end="")  
def read_gpt(disk):
    with open(disk.Name, "rb", buffering=0) as f:
        f.seek(512)
        data = f.read(512)
        print("GPT Header".center(50, "-"))
        print("Signature:", data[0:8].decode("utf-8"))
        print("Revision:", int.from_bytes(data[8:12], "little"))
        print("Header Size:", int.from_bytes(data[12:16], "little"))
        print("Header CRC32:",end="")
        for i in range(16, 20, 1):
            print(data[i:i+1].hex().upper(), end=" ")
        print()
        print("Reserved:", int.from_bytes(data[20:24], "little"))
        print("Current LBA:", int.from_bytes(data[24:32], "little"))
        print("Backup LBA:", int.from_bytes(data[32:40], "little"))
        print("First Usable LBA:", int.from_bytes(data[40:48], "little"))
        print("Last Usable LBA:", int.from_bytes(data[48:56], "little"))
        print("Disk GUID:", end="")
        for i in range(56, 72, 1): 
            print(data[i:i+1].hex().upper(), end=" ")
        print()
        print("Starting LBA of Partition Entry:", int.from_bytes(data[72:80], "little"))
        print("Number of Partition Entries:", int.from_bytes(data[80:84], "little"))
        print("Size of Partition Entry:", int.from_bytes(data[84:88], "little"))
        print("CRC32 of Partition Entry Array:", int.from_bytes(data[88:92], "little"))  
        print("GPT Header End".center(50, "-"))
        #Count entry different from 0

def count_partition_entry(disk):
    with open(disk.Name, "rb") as f:
        entry_count = 0
        for i in range(128):
            f.seek(1024 + 128 * i)
            data = f.read(128)
            if data[0] != 0:
                entry_count += 1
                print("Partition Entry", entry_count)
                print("Partition Type GUID:", data[0:16].hex())
                print("Unique Partition GUID:", data[16:32].hex())
                print("First LBA:", int.from_bytes(data[32:40], "little"))
                print("Last LBA:", int.from_bytes(data[40:48], "little"))
                print("Attribute Flags:", int.from_bytes(data[48:52], "little"))
                print("Partition Name:", data[56:128].decode("utf-16-le").rstrip("\x00"))
                if entry_count != 3:
                    open_volume(disk, int.from_bytes(data[32:40], "little"))
                    print("Partition Entry End".center(50, "-"))
                else:
                    print("Partition Entry End".center(50, "-"))
def open_volume(disk, lba):
    with open(disk.Name, "rb") as f:
        f.seek(lba * 512)
        data = f.read(512)
        file_system = data[3:11].hex()
        print("Volume Boot sector: ".center(50, " "))
        print("Jump Instruction:", data[0:3].hex())
        print("OEM ID (File system):",data[3:11].decode("utf-8") )
        if file_system == "4e54465320202020":
            print("BIOS Parameter Block: ".center(50, " "))
            print("Bytes per Sector:", int.from_bytes(data[11:13], "little"))
            print("Sectors per Cluster:", int.from_bytes(data[13:14], "little"))
            print("Reserved Sectors:", int.from_bytes(data[14:16], "little"))
            print("Media Descriptor:", int.from_bytes(data[21:22], "little"))
            print("Sectors per Track:", int.from_bytes(data[24:26], "little"))
            print("Number of Heads:", int.from_bytes(data[26:28], "little"))
            print("Hidden Sectors:", int.from_bytes(data[28:32], "little"))
            print("Signature:", data[36:40].hex())
            print("Total Sector:", int.from_bytes(data[40:48], "little"))
            print("Cluster Number of $MFT:", int.from_bytes(data[48:56], "little"))
            print("Cluster Number of $MFTMirr:", int.from_bytes(data[56:64], "little"))
            print("Clusters per File Record Segment:", int.from_bytes(data[64:68], "little"))
            print("Clusters per Index Buffer:", int.from_bytes(data[68:72], "little"))
            print("Volume Serial Number:", int.from_bytes(data[72:76], "little"))
            print("Checksum:", int.from_bytes(data[80:82], "little"))
            print("Bootstrapping Code: Data from 82 to 510")
            print("Signature:", data[510:512].hex().upper())
def read_MFT(disk, lba):
    with open(disk.Name, "rb") as f:
        f.seek(lba * 512)
        data = f.read(512)
        print("Master File Table".center(50, "-"))
        print("Signature:", data[0:4].decode("utf-8"))
        print("Fixup Array Offset:", int.from_bytes(data[4:6], "little"))
        print("Fixup Array Size:", int.from_bytes(data[6:8], "little"))
        print("Logfile Sequence Number:", int.from_bytes(data[8:16], "little"))
        print("Sequence Number:", int.from_bytes(data[16:18], "little"))
        print("Hard Link Count:", int.from_bytes(data[18:20], "little"))
        print("Offset to First Attribute:", int.from_bytes(data[20:22], "little"))
        print("Flags:", int.from_bytes(data[22:24], "little"))
        print("Used Size of MFT Entry:", int.from_bytes(data[24:26], "little"))
        print("Allocated Size of MFT Entry:", int.from_bytes(data[26:28], "little"))
        print("File Reference to Base File Record:", int.from_bytes(data[28:36], "little"))
        print("Next Attribute ID:", int.from_bytes(data[36:38], "little"))
        print("MFT Entry End".center(50, "-"))
def edit_hex_byte(data, offset, byte):
    return data[:offset] + bytes([byte]) + data[offset+1:]
#Main function
def main():
    if is_admin():
        pass
    else:
    # if sys.version_info[0] == 3:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        exit()
    # else:
        #ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(" ".join(sys.argv)), None, 1)
    diskDrive = disk_count()
    
    #Option to choose open disk or volume
    print("1. Open Disk")
    print("2. Read Sector")
    print("3. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        read_sector(diskDrive, 0)
        read_gpt(diskDrive)
        count_partition_entry(diskDrive)
        #return to main menu
        main()
    elif choice == "2":
        n = input("Sector: ")
        read_sector(diskDrive, n)
        main()
    elif choice == "3":
        exit()
    else:
        print("Invalid choice")
        exit()

if __name__ == "__main__":
    main()
#pause the screen
print("\nPress Enter to continue...")
input()