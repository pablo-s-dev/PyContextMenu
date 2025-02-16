import os
import sys
import winreg
from add_script_to_context_menu import run
import appdirs
import shutil

def get_asset_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_python_icon():

    app_dir = appdirs.user_data_dir("PyContextMenu", appauthor=False)

    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, "assets"), exist_ok=True)

    icon_dest = os.path.join(app_dir, "assets\\python.ico")

    if not os.path.exists(icon_dest):
        try:
            shutil.copy(get_asset_path("assets\\python.ico"), icon_dest)
        except Exception as e:
            print(f"Could not copy icon: {e}")
            return None

    return icon_dest


def create_command(script_key, mode, icon_path):


    command_key = winreg.CreateKey(script_key, "command")

    winreg.SetValue(command_key, "", winreg.REG_SZ, f'{sys.executable} "%1" {mode}')
    winreg.SetValueEx(script_key, "icon", 0, winreg.REG_SZ, icon_path)


    winreg.CloseKey(command_key)
    winreg.CloseKey(script_key)


def install_PyContextMenu():

    pyContextMenuIcon = "%systemroot%\\system32\\accessibilitycpl.dll,4"

    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    PyContextMenu = winreg.CreateKey(reg, f"Software\\Classes\\*\\shell\\PyContextMenu")
    winreg.SetValueEx(PyContextMenu, "MUIVerb", 0, winreg.REG_SZ, "Add this py script to the context menu of")
    winreg.SetValueEx(PyContextMenu, "SubCommands", 0, winreg.REG_SZ, "")
    winreg.SetValueEx(PyContextMenu, "Icon", 0, winreg.REG_SZ, pyContextMenuIcon)

    shell = winreg.CreateKey(PyContextMenu, "shell")

    script_keys = {
        '--files': winreg.CreateKey(shell, f"files"),
        '--folders': winreg.CreateKey(shell, f"folders"),
        '--background': winreg.CreateKey(shell, f"folder background"),
        '--all': winreg.CreateKey(shell, f"all")
    }

    icon_by_mode = {

        '--files': "%SystemRoot%\\system32\\shell32.dll,1",
        '--folders': "%SystemRoot%\\system32\\shell32.dll,3",
        '--background': "%SystemRoot%\\system32\\shell32.dll,34",
        '--all': "%SystemRoot%\\system32\\shell32.dll,19"
    }

    for mode, script_key in script_keys.items():

        create_command(script_key, mode, icon_by_mode[mode])

    winreg.CloseKey(reg)



if  len(sys.argv) > 1:

    script_icon_path = get_python_icon()

    run(script_icon_path)
else:
    # Installer mode

    install_PyContextMenu()
    print(f"PyContextMenu has been installed!\n")
    input("Press enter to continue...")
