import subprocess
import json
import os
import re
from typing import List, Dict

#####################################################     Admin Users     ####################################################################

def get_local_admins() -> List[Dict[str, str]]:
    """
    Executes a PowerShell script to retrieve local administrator accounts.
    
    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the admin account names.
    """
    powershell_script = """
    <#
    .SYNOPSIS
    Get-LocalAdmins.ps1 returns a list of local administrator accounts.
    .NOTES
    Next line is required by Kansa.ps1. It instructs Kansa how to handle the output from this script.
    OUTPUT tsv
    #>
    & net localgroup administrators | Select-Object -Skip 6 | ? { $_ -and $_ -notmatch "The command completed successfully" -and $_ -notmatch "^-+$" } | % { $o = "" | Select-Object Account; $o.Account = $_; $o }
    """

    # Execute the PowerShell script and capture the output
    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)

    # Check if the script executed successfully
    if result.returncode != 0:
        print(f"Error executing PowerShell script: {result.stderr}")
        return []

    # Parse the output and create a list of dictionaries
    output_lines: List[str] = result.stdout.strip().split("\n")
    admin_accounts: List[Dict[str, str]] = [{"Account": line.strip()} for line in output_lines]

    return admin_accounts

#####################################################     Local Users     ####################################################################

def get_local_users() -> List[Dict[str, str]]:
    """
    Retrieves information about local users using PowerShell.
    Returns a list of dictionaries containing user details (Disabled, Name, FullName, Caption, Domain, SID).
    """
    powershell_script = """
    Get-WmiObject win32_UserAccount | Select-Object -Property Disabled, Name, FullName, Caption, Domain, SID | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)

    # Check if the script executed successfully
    if result.returncode != 0:
        print(f"Error executing PowerShell script: {result.stderr}")
        return []

    users_data = json.loads(result.stdout)
    return users_data

#####################################################     Login History     ####################################################################

def get_login_history() -> List[Dict[str, str]]:
    """
    Retrieves the login history using PowerShell.
    Returns a list of dictionaries containing user and last logon details.
    """
    powershell_script = """
    Get-CimInstance -ClassName Win32_LoggedOnUser | 
      Select-Object @{Name='User';Expression={$_.Antecedent}}, 
                    @{Name='LastLogon';Expression={$_.LastLogon.ToString('MM/dd/yyyy hh:mm tt')}} |
    ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)

    # Check if the script executed successfully
    if result.returncode != 0:
        print(f"Error executing PowerShell script: {result.stderr}")
        return []

    login_history = json.loads(result.stdout)
    return login_history

#####################################################     Last Added Processes     ####################################################################

def get_last_added_processes() -> List[Dict[str, str]]:
    """
    Retrieves the last 20 added processes on the system using PowerShell.
    Returns a list of dictionaries containing file path and creation time.
    """
    powershell_script = """
    $limit = 20
    $files = Get-ChildItem -Path C:\\ -File -Recurse | Sort-Object CreationTime -Descending | Select-Object -First $limit
    $files | ForEach-Object {
        $file = $_.FullName
        $created = $_.CreationTime
        [PSCustomObject]@{
            File = $file
            Created = $created
        }
    } | Format-Table -AutoSize
    """

    try:
        output = subprocess.check_output(["powershell.exe", "-Command", powershell_script], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        output = e.output

    last_added_processes = []
    for line in output.splitlines():
        if line.startswith("File"):
            continue
        elif line.strip() == "":
            continue
        else:
            try:
                file_path, created_time = re.split(r"\s+", line.strip(), maxsplit=1)
                last_added_processes.append({
                    "File": file_path,
                    "Created": created_time
                })
            except ValueError:
                pass

    return last_added_processes

def merge_and_save_to_json() -> None:
    """
    Merges the admin accounts, local users, login history, and last added processes data into a single dictionary and saves it to a JSON file.
    """
    merged_data = {
        "admin_accounts": get_local_admins(),
        "local_users": get_local_users(),
        "login_history": get_login_history(),
        "last_added_processes": get_last_added_processes()
    }

    # Get the directory of the currently executing script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Create the full path for the JSON file
    json_file_path = os.path.join(current_directory, "security_pt1.json")



    # Save the output to the JSON file
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(merged_data, json_file, indent=4, ensure_ascii=False)

    print(f"All data merged and saved to {full_file_path}")

def main():
    merge_and_save_to_json()

if __name__ == "__main__":
    main()