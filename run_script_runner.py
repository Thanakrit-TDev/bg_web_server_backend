import subprocess
import os

def run_batch_file():
    script_path = 'run_script.bat'
    result = subprocess.run(script_path, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == "__main__":
    if os.name == 'nt':  # Windows
        run_batch_file()
    else:
        print("This script is designed for Windows. Please use the appropriate script for your OS. 555")
