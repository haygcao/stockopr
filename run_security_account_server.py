import os
import subprocess


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    script = 'security_account_server.py'

    py = str(os.path.join(root_dir, 'venv', 'Scripts', 'python.exe'))
    script_path = os.path.join(root_dir, script)

    os.environ['PYTHONPATH'] = root_dir
    subprocess.Popen([py, script_path], creationflags=subprocess.DETACHED_PROCESS, cwd=root_dir)
