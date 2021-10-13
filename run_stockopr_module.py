import os
import subprocess
import sys

if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    # script = 'security_account_server.py'

    # root_dir = r'D:\workspace\stockopr'
    script = sys.argv[1]
    script_path = os.path.join(root_dir, script)

    os.environ['PYTHONPATH'] = root_dir

    if sys.platform == 'win32':
        py = str(os.path.join(root_dir, 'venv', 'Scripts', 'python.exe'))
        subprocess.Popen([py, script_path], creationflags=subprocess.DETACHED_PROCESS, cwd=root_dir)
    else:
        py = str(os.path.join(root_dir, 'venv', 'bin', 'python'))
        subprocess.Popen([py, script_path], cwd=root_dir)
