import datetime
import json
import socket
import subprocess
import os
import psutil
import pytz


def get_all_gpu_info():
    try:
        # Run the 'nvidia-smi' command to get GPU information for all GPUs
        result = subprocess.check_output(["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total,memory.free,memory.used", "--format=csv,noheader,nounits"])
        gpu_info = [line.strip().split(", ") for line in result.decode("utf-8").split("\n") if line.strip()]

        formatted_info = []
        for gpu in gpu_info:
            formatted_gpu = {
                "name": gpu[1],
                "driver_version": gpu[2],
            }
            formatted_info.append(formatted_gpu)

        return formatted_info
    except subprocess.CalledProcessError:
        print("Error retrieving GPU information.")
        return []

def get_bios_info():
    """
    Retrieves BIOS information using PowerShell.
    Returns a dictionary containing the BIOS name, version, and SMBIOS BIOS version.
    """
    powershell_script = """
    get-wmiobject -query "SELECT * FROM Win32_BIOS" | select-object Name,Version,SMBIOSBIOSVersion | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_cpu_info():
    """
    Retrieves CPU information using PowerShell.
    Returns a list of dictionaries containing the CPU manufacturer, name, current clock speed, and L2 cache size.
    """
    powershell_script = """
    get-wmiobject -query "SELECT * FROM Win32_Processor" | select-object Manufacturer,Name,CurrentClockSpeed,L2CacheSize | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_computer_system_info():
    """
    Retrieves computer system information using PowerShell.
    Returns a dictionary containing the computer name, domain, description, manufacturer, model, number of processors, total physical memory, system type, primary owner name, and username.
    """
    powershell_script = """
    get-wmiobject -query "SELECT * FROM Win32_ComputerSystem" | select-object Name,Domain,Description,Manufacturer,Model,NumberOfProcessors,TotalPhysicalMemory,SystemType,PrimaryOwnerName,UserName | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_operating_system_info():
    """
    Retrieves operating system information using PowerShell.
    Returns a dictionary containing the operating system caption, build number, version, serial number, service pack major version, and install date.
    """
    powershell_script = """
    get-wmiobject -query "SELECT * FROM Win32_OperatingSystem" | select-object Caption,BuildNumber,Version,SerialNumber,ServicePackMajorVersion,InstallDate | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_drive_info():
    """
    Get drive information using PowerShell.
    Returns a list of dictionaries containing drive name, free space, used space, and total space.
    """
    powershell_script = """
    # Get all logical drives
    $drives = Get-PSDrive -PSProvider FileSystem

    # Output the drives with their details
    $drive_info = @()
    foreach ($drive in $drives) {
        $driveName = $drive.Name
        $freeSpaceGB = "{0:N2}" -f ($drive.Free / 1GB)
        $usedSpaceGB = "{0:N2}" -f ($drive.Used / 1GB)
        $totalSpaceGB = $usedSpaceGB + $freeSpaceGB
        $driveObject = @{
            "Drive Name" = $driveName
            "$driveName Free Space (GB)" = $freeSpaceGB
            "$driveName Used Space (GB)" = $usedSpaceGB
            "$driveName Total Space (GB)" = $totalSpaceGB
        }
        $drive_info += $driveObject
    }
    @{ "drive_info" = $drive_info } | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_drive_types():
    """
    Get drive types (SSD or HDD) using PowerShell.
    Returns a list of dictionaries containing the friendly name, serial number, and media type.
    """
    powershell_script = """
    Get-WmiObject -Class MSFT_PhysicalDisk -Namespace root\Microsoft\Windows\Storage | Select FriendlyName, SerialNumber, @{ Name='MediaType'; Expression={ switch ($_.MediaType) { 3 {'HDD'} 4 {'SSD'} } } } | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_system_uptime():
    """
    Get the system uptime using PowerShell.
    Returns a string representing the uptime.
    """
    powershell_script = """
    # Get the system uptime
    $uptime = (Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime
    Write-Output $uptime | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is not None:
        percent = battery.percent
        plugged = "Plugged In" if battery.power_plugged else "Not Plugged In"
        battery_info = [{"percentage": percent, "status": plugged}]
        return battery_info
    else:
        return []

def get_ram_info():
    memory_info = psutil.virtual_memory()
    ram_info = [{
        "used_percent": f"{memory_info.percent} %",
        "total_gb": round(memory_info.total / (1024 ** 3), 2),
        "available_gb": round(memory_info.available / (1024 ** 3), 2),
        "used_gb": round(memory_info.used / (1024 ** 3), 2),
        "free_gb": round(memory_info.free / (1024 ** 3), 2)
    }]
    return ram_info

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_mac_address(ip_address):
    try:
        pid = subprocess.Popen(["arp", "-n", ip_address], stdout=subprocess.PIPE)
        output = pid.communicate()[0].decode("utf-8")
        mac_address = output.split()[2]
        return mac_address
    except:
        return ""

def get_local_time_zone():
    local_tz = pytz.timezone("Africa/Cairo")
    now = datetime.datetime.now(local_tz)
    tz_info = now.strftime("%I:%M %p %Z (UTC%z) %Z (%z DST)")
    return [{"time_zone": tz_info}]

def save_to_json(data):
    with open("device_info.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def main():
    # Get computer information
    gpu_info = get_all_gpu_info()
    bios_info = get_bios_info()
    cpu_info = get_cpu_info()
    computer_system_info = get_computer_system_info()
    operating_system_info = get_operating_system_info()
    drive_info = get_drive_info()["drive_info"]
    drive_types = get_drive_types()
    system_uptime = get_system_uptime()

    # Combine all information into a single dictionary
    computer_info = {
        "GPU_Info": gpu_info,
        "bios_info": bios_info,
        "cpu_info": cpu_info,
        "computer_system_info": computer_system_info,
        "operating_system_info": operating_system_info,
        "drive_info": drive_info,
        "drive_types": drive_types,
        "system_uptime": system_uptime,
    }

    # Get the directory of the currently executing script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Create the full path for the JSON file
    json_file_path = os.path.join(current_directory, "computer_info.json")

    # Save the output to the JSON file
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(computer_info, json_file, indent=4, ensure_ascii=False)

    print(f"Computer information saved to {json_file_path}")

import os
import json

def main():
    # Get computer information
    gpu_info = get_all_gpu_info()
    bios_info = get_bios_info()
    cpu_info = get_cpu_info()
    computer_system_info = get_computer_system_info()
    operating_system_info = get_operating_system_info()
    drive_info = get_drive_info()["drive_info"]
    drive_types = get_drive_types()
    system_uptime = get_system_uptime()

    # Get device information
    device_info = {}
    battery_status = get_battery_status()
    device_info["battery_status"] = battery_status
    ram_info = get_ram_info()
    device_info["ram_info"] = ram_info
    ip_address = get_ip_address()
    mac_address = get_mac_address(ip_address)
    device_info["ip_mac_info"] = [{"ip_address": ip_address, "mac_address": mac_address}]
    time_zone_info = get_local_time_zone()
    device_info["time_zone_info"] = time_zone_info

    # Combine all information into a single dictionary
    computer_info = {
        "GPU_Info": gpu_info,
        "bios_info": bios_info,
        "cpu_info": cpu_info,
        "computer_system_info": computer_system_info,
        "operating_system_info": operating_system_info,
        "drive_info": drive_info,
        "drive_types": drive_types,
        "system_uptime": system_uptime,
        "device_info": device_info
    }

    # Get the directory of the currently executing script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Create the full path for the JSON file
    json_file_path = os.path.join(current_directory, "computer_info.json")

    # Save the output to the JSON file
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(computer_info, json_file, indent=4, ensure_ascii=False)

    print(f"Computer information saved to {json_file_path}")

if __name__ == "__main__":
    main()