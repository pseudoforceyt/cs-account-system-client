import os
from i18n import firstrun
from yaml import dump as dumpyaml
from . import encryption as e
from . import db_handler as db
try: 
    from tkinter import filedialog
except:
    pass

def get_client_dir():
    while True:
        try:
            # Open GUI file picker if possible
            print(firstrun.savedata.gui)
            spath = filedialog.askdirectory()
        except:
            print(firstrun.savedata.nogui)
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
                spath = input(f"{firstrun.savedata.not_a_dir}:\n")
            elif not os.path.exists(spath):
                print(firstrun.savedata.creating, end=' ')
                try:
                    os.mkdir(spath)
                except OSError as e:
                    print(f"{firstrun.savedata.error}:\n{e}")
                    spath = input(f"{firstrun.savedata.input_writable}:\n")
                else:
                    print(firstrun.savedata.created)
                    break
        if not os.path.exists(f'{spath}/creds'):
            os.mkdir(f'{spath}/creds')
            break
        elif os.path.exists(f'{spath}/creds'):
            print(firstrun.savedata.data_exists)
    return spath

def save_chat_keypair(fkey, workingdir):
    prkey, pubkey = e.create_rsa_key_pair()
    pem_prkey, pem_pubkey = e.ser_key_pem(prkey, 'private'), e.ser_key_pem(pubkey, 'public')
    en_pem_prkey = fkey.encrypt(pem_prkey)
    with open(f'{workingdir}/creds/chat_privatekey', 'wb') as f:
        f.write(en_pem_prkey)
    with open(f'{workingdir}/creds/chat_publickey', 'wb') as f:
        f.write(pem_pubkey)

def main():
    print(firstrun.welcome_message)
    print(firstrun.setup_client_dir)
    workingdir = setup_client_dir()
    fkey, passwd = e.fernet_initkey(workingdir)
    save_chat_keypair(fkey, workingdir)
    db.create_db(workingdir) # todo : add password protection
    del passwd
    del fkey
    print("You will be able to change these later")
    host = input("Enter Homeserver Address: ")
    port = int(input("Enter Homeserver Port: "))
    with open(f'{os.path.dirname(os.path.abspath(__file__))}/../config.yml', 'w') as fi:
        config = {'working_directory': workingdir, 'homeserver_address': host, 'homeserver_port': port}
        fi.write(dumpyaml(config))