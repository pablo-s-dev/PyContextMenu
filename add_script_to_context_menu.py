import os
import sys
import winreg

def create_command(shell_key, file_path, name, accepts_arg_path = True):

    """
    Create the command key for the given mode
    :param shell_key: The key to create the command key under
    :param file_path: The path to the script
    :param name: The name of the script
    :param accepts_arg_path: Whether the script accepts a path as an argument
    :return: None
    """

    if not os.path.exists(file_path):
        print(f"{file_path} not found")
        input("Press enter to continue...")
        return

    if not os.path.isfile(file_path):
        print(f"{file_path} is not a file")
        input("Press enter to continue...")
        return

    if not file_path.endswith('.py'):
        print(f"{file_path} is not a python script")
        input("Press enter to continue...")
        return

    try:
        script_key = winreg.CreateKey(shell_key, name)
    except FileNotFoundError:
        print(f"Could not create key {name}")
        input("Press enter to continue...")
        return

    command_key = winreg.CreateKey(script_key, "command")

    if accepts_arg_path:

        winreg.SetValue(command_key, "", winreg.REG_SZ, f'cmd.exe /c python.exe "{file_path}" "%1"')

    else:
        winreg.SetValue(command_key, "", winreg.REG_SZ, f'cmd.exe /c python.exe "{file_path}"')

    winreg.CloseKey(command_key)
    winreg.CloseKey(script_key)


def add_to_context_menu(file_path, name, chosen_paths: dict):

    """
    Add the script to the context menu
    :param file_path: The path to the script
    :param name: The name of the script
    :param chosen_paths: The paths to add the script to
    :return
    """


    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)


    for mode, key_path in chosen_paths.items():

        # It will just open the key if it already exists
        shell_key = winreg.CreateKey(reg, key_path)
        if not shell_key:
            print(f"Could not open key {key_path}")
            input("Press enter to continue...")
            continue
        create_command(shell_key, file_path, name, accepts_arg_path= mode != '--background')
        winreg.CloseKey(shell_key)

    if reg:
        winreg.CloseKey(reg)

# def get_progid_for_extension(ext: str) -> str | None:
#     """
#     Given a file extension like ".py",
#     returns the default value (ProgID) under HKCR\.py
#     or None if not found or not set.
#     """
#     # Ensure the extension starts with a dot
#     if not ext.startswith("."):
#         ext = "." + ext

#     try:
#         with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
#             progid = winreg.QueryValue(key, None)
#             return progid  # e.g. "Python" or "Python.File"
#     except FileNotFoundError:
#         return None
#     except OSError:
#         return None

def get_shell_paths(target_extension = "*"):

    """
    Get the paths to the shell keys
    :param target_extension: The target extension
    :return: The paths to the shell keys
    """

    # progid = get_progid_for_extension(target_extension)

    # print(progid)

    # if not progid:
    #     print(f"Could not find ProgID for extension {target_extension}")
    #     input("Press enter to continue...")
    #     return

    all_shell_paths = {
        '--files': f"SOFTWARE\\Classes\\{target_extension}\\shell",
        '--folders': "SOFTWARE\\Classes\\Directory\\shell",
        '--background': "SOFTWARE\\Classes\\Directory\\background\\shell",
    }
    return all_shell_paths

def run():

    """
    Runs the script
    :return: None
    """

    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    script_path = os.path.abspath(sys.argv[1])
    choice = sys.argv[2]

    # It seems that I need to write the shell command under HKCR to target file extensions
    # so I will remove this feature for now
    # target_extension = sys.argv[3] if len(sys.argv) > 3 else input("Enter the target extension (e.g. 'py' or '*' to target every file): ")

    # target_extension = target_extension.lower().replace("'", "").replace('"', "")

    # if not target_extension.endswith('.') and target_extension != '*':
    #     target_extension = f".{target_extension}"
    target_extension = "*"

    all_shell_paths = get_shell_paths(target_extension)

    # if not all_shell_paths:
    #     return

    chosen_paths = {}
    if choice == '--all':
        chosen_paths = all_shell_paths
    else:
        chosen_paths = {choice: all_shell_paths[choice]}

    # remove dir and extension
    name = script_path.replace(f'{os.path.dirname(script_path)}\\', '').replace('.py', '')

    add_to_context_menu(script_path, name, chosen_paths)
    print(f"Script {name} added to context menu!\n")
    input("Press enter to continue...")

if __name__ == '__main__':
    run()
