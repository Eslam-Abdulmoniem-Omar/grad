import winreg
import subprocess
import json
import os

def list_startup_programs():
    """List all programs that start automatically when the system boots up."""
    startup_programs = []
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")

    try:
        i = 0
        while True:
            program_name, program_path, _ = winreg.EnumValue(reg_key, i)
            startup_programs.append({"name": program_name, "path": program_path})
            i += 1
    except WindowsError:
        pass

    winreg.CloseKey(reg_key)
    return startup_programs

def get_installed_apps():
    """
    Retrieves information about installed applications using PowerShell.
    Returns a list of dictionaries, each containing app details (Name, Version, Vendor).
    """
    powershell_script = """
    # Get the list of installed programs
    $programs = Get-WmiObject -Class Win32_Product

    # Select the Name and Version properties
    $selectedProperties = $programs | Select-Object Name, Version, Vendor

    # Convert the output to JSON
    $selectedProperties | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    apps_data = json.loads(result.stdout)
    return apps_data

def save_to_json(data, json_file_path):
    """
    Saves the provided data to a JSON file.
    """
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def main():
    json_file_path = "apps_info.json"  # Specify the desired file path

    # Get installed apps and startup programs
    installed_apps = get_installed_apps()
    startup_programs = list_startup_programs()

    # Combine the data into a single dictionary
    data = {
        "installed_apps": installed_apps,
        "startup_apps": startup_programs
    }

    # Save the output to the JSON file
    save_to_json(data, json_file_path)

    print("System information saved to apps_info.json")

if __name__ == "__main__":
    main()