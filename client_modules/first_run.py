import os
from i18n import firstrun, savedata
from yaml import dump as dumpyaml
from . import encryption as e

try:
    from tkinter import filedialog
except:
    pass


def get_client_dir():
    while True:
        try:
            # Open GUI file picker if possible
            print(savedata.gui)
            spath = filedialog.askdirectory()
        except:
            print(savedata.nogui)
            spath = input().rstrip('/\\')
        finally:
            break
    return spath


def setup_client_dir():
    while True:
        while True:
            spath = get_client_dir()
            # Do nothing if folder exists
            if os.path.exists(spath) and os.path.isdir(spath):
                break
            # If either the path leads to a file or is not writable (or invalid)
            elif os.path.exists(spath) and not os.path.isdir(spath):
                spath = input(f"{savedata.not_a_dir}:\n")
            elif not os.path.exists(spath):
                print(savedata.creating, end=' ')
                try:
                    os.mkdir(spath)
                except OSError as error:
                    print(f"{savedata.error}:\n{error}")
                    spath = input(f"{savedata.input_writable}:\n")
                else:
                    print(savedata.created)
                    break
        if not os.path.exists(f'{spath}/creds'):
            os.mkdir(f'{spath}/creds')
            break
        elif os.path.exists(f'{spath}/creds'):
            print(savedata.data_exists)
    return spath


def main():
    print(firstrun.welcome_message)
    print(firstrun.setup_client_dir)
    workingdir = setup_client_dir()
    print(firstrun.config_modinfo)
    host = input(firstrun.hs_addr)
    port = int(input(firstrun.hs_port))
    with open(f'{os.path.dirname(os.path.abspath(__file__))}/../config.yml', 'w') as fi:
        config = {'working_directory': workingdir, 'homeserver_address': host, 'homeserver_port': port}
        fi.write(dumpyaml(config))
