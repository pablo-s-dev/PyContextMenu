import os
import sys
import winreg
from add_script_to_context_menu import run

def create_command(script_key, mode):


    command_key = winreg.CreateKey(script_key, "command")

    winreg.SetValue(command_key, "", winreg.REG_SZ, f'{sys.executable} "%1" {mode}')


    winreg.CloseKey(command_key)
    winreg.CloseKey(script_key)




def add_to_context_menu(name):

    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    PyContextMenu = winreg.CreateKey(reg, f"Software\\Classes\\*\\shell\\{name}")
    winreg.SetValueEx(PyContextMenu, "MUIVerb", 0, winreg.REG_SZ, "Add this py script to the context menu of")
    winreg.SetValueEx(PyContextMenu, "SubCommands", 0, winreg.REG_SZ, "")

    shell = winreg.CreateKey(PyContextMenu, "shell")

    script_keys = {
        '--files': winreg.CreateKey(shell, f"files"),
        '--folders': winreg.CreateKey(shell, f"folders"),
        '--background': winreg.CreateKey(shell, f"folder background"),
        '--all': winreg.CreateKey(shell, f"all")
    }

    for mode, script_key in script_keys.items():

        create_command(script_key, mode)

    winreg.CloseKey(reg)


name = "PyContextMenu"

if  len(sys.argv) > 1:
    run()
else:
    # Installer mode
    add_to_context_menu(name)
    print(f"PyContextMenu has been installed!\n")
    input("Press enter to continue...")
