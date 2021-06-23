import os
import subprocess


if __name__ == "__main__":
    script = 'security_account_server.py'
    root_dir = os.path.dirname(__file__)
    monitor_path = os.path.join(root_dir, script)
    os.environ['PYTHONPATH'] = root_dir
    py = str(os.path.join(root_dir, 'venv', 'Scripts', 'python.exe'))
    subprocess.Popen([py, monitor_path], creationflags=subprocess.DETACHED_PROCESS)
    # subprocess.run([py, monitor_path])
