import winreg as reg
import os


def add_to_registry():
    pth = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    pth = os.path.abspath(pth)

    s_name = "security_account_server.py"
    address = os.path.join(pth, s_name)
    
    py = str(os.path.join(pth, 'venv', 'Scripts', 'python.exe'))
    cmd = '"{}" "{}"'.format(py, address)

    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"

    opened_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(opened_key, "any_name", 0, reg.REG_SZ, cmd)
    reg.CloseKey(opened_key)


def modify_mysqld_exec_path():
    key = reg.HKEY_LOCAL_MACHINE
    key_value = r"SYSTEM\CurrentControlSet\Services\MySQL"

    opened_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(opened_key, "ImagePath", 0, reg.REG_SZ, r'"C:\Program Files\MySQL\bin\mysqld" MySQL')
    reg.CloseKey(opened_key)


if __name__ == "__main__":
    add_to_registry()
    # modify_mysqld_exec_path()
