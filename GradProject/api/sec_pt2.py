import subprocess
import json
import os
import hashlib

# Define the PowerShell scripts
smb_sessions_script = """
# Get the list of SMB sessions
$smbSessions = Get-SmbSession

# Check if there are any active SMB sessions
if ($smbSessions) {
    # Display the SMB sessions
    $smbSessions | ConvertTo-Json -Compress
} else {
    # Display a message
    Write-Output "No active smbSessions"
}
"""

bit_locker_script = """
# PowerShell script to check if the hard drive is encrypted using BitLocker
# Run the Get-BitLockerVolume cmdlet to get information about BitLocker-protected volumes
$bitlockerInfo = Get-BitLockerVolume

# Check if any volumes are encrypted
if ($bitlockerInfo.Count -eq 0) {
    Write-Output "No BitLocker-protected volumes found."
} else {
    foreach ($volume in $bitlockerInfo) {
        Write-Output "Volume $($volume.MountPoint) is encrypted."
    }
}
"""

ip_sec_check_script = r"""
$apiKey = "da596e8a9b9f738b5ef954837a7b8c161112a3798d58c9b5629819bfd2316a6dbcc4932a4169cfb5"

try {
    # Check for administrator privileges
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "Error: This script requires administrative privileges. Run PowerShell as an administrator and try again."
    }

    # Get established connections excluding localhost
    $connections = Get-NetTCPConnection | Where-Object { $_.State -eq 'Established' -and $_.RemoteAddress -ne "127.0.0.1" -and $_.RemoteAddress -ne "::1" }

    $maliciousIPs = @()

    if ($connections) {
        $connections | ForEach-Object {
            $remoteAddress = $_.RemoteAddress
            $remotePort = $_.RemotePort
            $processId = $_.OwningProcess

            try {
                $abuseIpDetails = Invoke-RestMethod -Uri "https://api.abuseipdb.com/api/v2/check" -Method Get -Headers @{ "Key" = $apiKey } -Body @{ "ipAddress" = $remoteAddress } -ErrorAction Stop

                if ($abuseIpDetails.data.abuseConfidenceScore -ge 90) {
                    $maliciousIPs += [PSCustomObject]@{
                        "IP Address" = $remoteAddress
                        "Process ID" = $processId
                    }
                }
            } catch {
                # Suppress error output within the loop
            }
        }
    }

    # Format the output as JSON
    $jsonOutput = $maliciousIPs | ConvertTo-Json -Compress
    Write-Output $jsonOutput
} catch {
    # Suppress error output in main try block
}
"""

def get_running_processes():
    try:
        # Execute the tasklist command and capture the output
        process_list = subprocess.check_output(["tasklist"], universal_newlines=True)
        return process_list.splitlines()
    except subprocess.CalledProcessError:
        print("Error executing tasklist command.")
        return []

def check_malicious_processes():
    # Get a list of all running process names
    running_processes = get_running_processes()

    # Read the contents of the "mali_info.txt" file
    mali_info_file = "mali_info.txt"
    if os.path.exists(mali_info_file):
        with open(mali_info_file, "r") as f:
            malicious_process_names = set(line.strip() for line in f.readlines())
    else:
        print(f"Error: {mali_info_file} not found.")
        return

    # Create a dictionary to store the malicious process data
    malicious_data = {"malicious_process": []}

    # Check for matches between running processes and malicious process names
    for process_line in running_processes[3:]:  # Skip the first 3 lines (header)
        process_info = process_line.split()
        process_name, process_pid, process_memory = process_info[0], process_info[1], process_info[4]
        if process_name in malicious_process_names:
            malicious_data["malicious_process"].append({
                "name": process_name,
                "pid": process_pid,
                "memory_usage": process_memory
            })

    return malicious_data


import subprocess
import hashlib
import json

def get_process_matches():
    """
    Retrieves process hashes, compares them to hashes from a text file,
    and saves matching results to a JSON file.
    """
    # Run the PowerShell script to get process hashes
    powershell_script = """
    # Get a list of running processes
$processes = Get-Process

# Iterate through each process
foreach ($process in $processes) {
    # Calculate the hash value of the process executable file
    $hash = Get-FileHash -Path $process.Path -Algorithm SHA256

    # Display process information
    Write-Host "Name: $($process.Name)"
    Write-Host "ID: $($process.Id)"
    Write-Host "PID: $($process.ParentId)"
    Write-Host "SHA256 Hash: $($hash.Hash)"
    Write-Host "--------------------------"
}

    """

    # Execute the PowerShell script
    process = subprocess.Popen(["powershell", "-Command", powershell_script], stdout=subprocess.PIPE)
    output, _ = process.communicate()

    # Parse the output to get process names, hashes, and PIDs
    process_info = {}
    for line in output.decode("utf-8").splitlines():
        if line.startswith("Name:"):
            name = line.split(":")[1].strip()
        elif line.startswith("ID:"):
            pid = int(line.split(":")[1].strip())
        elif line.startswith("SHA256 Hash:"):
            hash_value = line.split(":")[1].strip()
            process_info[name] = {"hash": hash_value, "pid": pid}

    # Read hashes from the text file
    with open("hashes.txt", "r") as file:
        file_hashes = [line.strip() for line in file]

    # Compare process hashes with file hashes
    matches = []
    for name, info in process_info.items():
        if info["hash"] in file_hashes:
            matches.append({"name": name, "hash": info["hash"], "pid": info["pid"]})

    # Save matches to a JSON file
    with open("process_matches.json", "w") as json_file:
        json.dump({"malicious_process_by_hash": matches}, json_file, indent=4)

    print("Process matches saved to process_matches.json")

# Call the function to execute the process
get_process_matches()





def main():
    # Get the current directory
    current_dir = os.getcwd()
    
    #malicous process by hash
    get_process_matches()

    # Construct the JSON file path
    json_file_path = os.path.join(current_dir, "output.json")

    # Get SMB sessions
    smb_sessions_result = subprocess.run(["powershell", "-Command", smb_sessions_script], capture_output=True, text=True)
    if smb_sessions_result.stdout.strip() == "No active smbSessions":
        smb_sessions_data = "No active smbSessions"
    else:
        smb_sessions_data = json.loads(smb_sessions_result.stdout)

    # Get BitLocker encryption status
    bit_locker_result = subprocess.run(["powershell", "-Command", bit_locker_script], capture_output=True, text=True)
    bit_locker_output = bit_locker_result.stdout.strip()
    if "No BitLocker-protected volumes found." in bit_locker_output:
        bit_locker_data = {
            "status": "success",
            "message": "No BitLocker-protected volumes found.",
            "encrypted_volumes": []
        }
    else:
        encrypted_volumes = []
        for line in bit_locker_output.splitlines():
            if "Volume" in line:
                volume = line.split("Volume ")[1].split(" is encrypted.")[0]
                encrypted_volumes.append(volume)
        bit_locker_data = {
            "status": "success",
            "message": "BitLocker-protected volumes found.",
            "encrypted_volumes": encrypted_volumes
        }

    # Check for malicious IP connections
    ip_sec_result = subprocess.run(["powershell", "-Command", ip_sec_check_script], capture_output=True, text=True)
    if ip_sec_result.stdout.strip():
        ip_sec_data = json.loads(ip_sec_result.stdout)
    else:
        ip_sec_data = []

    # Get malicious process data
    malicious_process_data = check_malicious_processes()

    # Combine all data into a single dictionary
    output_data = {
        "smb_sessions": smb_sessions_data,
        "bit_locker": bit_locker_data,
        "ip_security": ip_sec_data,
        "malicious_processes": malicious_process_data
    }

    # Save the output to the JSON file
    with open(json_file_path, "w") as json_file:
        json.dump(output_data, json_file, indent=4)

    print(f"Output saved to {json_file_path}")

if __name__ == "__main__":
    main()