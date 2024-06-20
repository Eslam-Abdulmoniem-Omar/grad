import subprocess
import json
import os

def get_running_processes():
    """
    Retrieves information about running processes using PowerShell.
    Returns a list of dictionaries, each containing process details.
    """
    powershell_script = """
    # Get all running processes
    $processes = Get-Process

    # Output the processes with their details
    $processes | ForEach-Object {
        $processName = $_.Name
        $processId = $_.Id
        $cpuUsage = $_.CPU
        $memoryUsage = $_.PM
        [PSCustomObject]@{
            "Process Name" = $processName
            "Process ID" = $processId
            "CPU Usage" = $cpuUsage
            "Memory Usage" = $memoryUsage
        }
    } | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    processes_data = json.loads(result.stdout)
    return processes_data

def get_last_active_process():
    """
    Retrieves information about the last opened processes using PowerShell.
    Returns a list of dictionaries, each containing process details (Name, StartTime).
    """
    powershell_script = """
    # Get the list of running processes
    $processes = Get-Process

    # Sort the processes by start time in descending order
    $sortedProcesses = $processes | Sort-Object StartTime -Descending

    # Select the first 10 processes and display only the name and start time
    $lastOpenedApplications = $sortedProcesses | Select-Object -First 10 | Select-Object Name, StartTime

    # Convert the result to JSON
    $lastOpenedApplications | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    processes_data = json.loads(result.stdout)
    return processes_data

def get_top_cpu_processes():
    powershell_script = """
    # Get all running processes
    $processes = Get-Process

    # Sort the processes by CPU usage in descending order and select the top 10
    $topCPUProcesses = $processes | Sort-Object -Property CPU -Descending | Select-Object -First 10

    # Output the top CPU processes with their details
    $topCPUProcesses | ForEach-Object {
        $processName = $_.Name
        $processId = $_.Id
        $cpuUsage = $_.CPU
        $memoryUsage = $_.PM
        [PSCustomObject]@{
            "Process Name" = $processName
            "Process ID" = $processId
            "CPU Usage" = $cpuUsage
            "Memory Usage" = $memoryUsage
        }
    } | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    processes_data = json.loads(result.stdout)
    return processes_data

def get_top_memory_processes():
    powershell_script = """
    # Get all running processes
    $processes = Get-Process

    # Sort the processes by memory usage in descending order and select the top 10
    $topMemoryProcesses = $processes | Sort-Object -Property PM -Descending | Select-Object -First 10

    # Output the top memory processes with their details
    $topMemoryProcesses | ForEach-Object {
        $processName = $_.Name
        $processId = $_.Id
        $cpuUsage = $_.CPU
        $memoryUsage = $_.PM
        [PSCustomObject]@{
            "Process Name" = $processName
            "Process ID" = $processId
            "CPU Usage" = $cpuUsage
            "Memory Usage" = $memoryUsage
        }
    } | ConvertTo-Json
    """

    result = subprocess.run(["powershell", "-Command", powershell_script], capture_output=True, text=True)
    processes_data = json.loads(result.stdout)
    return processes_data

def save_to_json(data, json_file_path):
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def main():
    json_file_path = "combined_proc_info.json"  # Specify the desired file path

    # Get running processes
    all_processes = get_running_processes()

    # Get last active processes
    last_active_processes = get_last_active_process()

    # Get top CPU processes
    top_cpu_processes = get_top_cpu_processes()

    # Get top memory processes
    top_memory_processes = get_top_memory_processes()

    # Combine all the data into a single dictionary
    combined_data = {
        "all_process": all_processes,
        "last_active_process": last_active_processes,
        "proc_by_cpu": top_cpu_processes,
        "proc_by_mem": top_memory_processes
    }

    # Save the combined data to the JSON file
    save_to_json(combined_data, json_file_path)

    print("Combined process information saved to combined_proc_info.json")

if __name__ == "__main__":
    main()