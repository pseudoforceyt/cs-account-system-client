import asyncio
import websockets
import os
from cryptography.hazmat.primitives import serialization as s
from client_modules import encryption as en
from client_modules import packet_handler as p
from client_modules import cli_menus as cli
from client_modules import first_run
from uuid import uuid4
import i18n
from yaml import safe_load as loadyaml
from yaml import dump as dumpyaml
import pickle
from sys import exit


async def send_message(websocket, message):
    if message:
        await websocket.send(message)


async def recv_message(websocket, message):
    inpacket = en.decrypt_data(message, CLIENT_CREDS['client_eprkey'])
    # handle check
    outpacket = await p.handle(SERVER_CREDS, CLIENT_CREDS, websocket, inpacket)
    if not outpacket:
        await websocket.send(outpacket)
    else:
        pass


def execute_firstrun():
    first_run.main()
    print(i18n.firstrun.exit)
    exit()


def check_missing_config(f, yaml, config):
    try:
        if yaml[config] is None:
            print(i18n.firstrun.prompt1 + config)
            if config == 'working_directory':
                print(i18n.firstrun.prompt2)
                while True:
                    choice = input("(Y / N) > ")
                    if choice.lower() == 'y':
                        print(i18n.firstrun.exec)
                        f.close()
                        os.remove(f'{rootdir}/config.yml')
                        first_run.main()
                        print(i18n.firstrun.exit)
                        exit()
                    elif choice.lower() == 'n':
                        fill_missing_config(f, yaml, 'working_directory')
                        break
            else:
                fill_missing_config(f, yaml, config)
    except KeyError:
        print(i18n.firstrun.prompt1 + config)
        fill_missing_config(f, yaml, config)


def fill_missing_config(f, yaml, config):
    print(i18n.firstrun.fix_missing, config)
    yaml[config] = input('\n> ')
    if config in ['homeserver_port', 'any_other_int_type_config']:
        yaml[config] = int(yaml[config])
    f.seek(0)
    f.write(dumpyaml(yaml))


async def main(host, port):
    uri = f"ws://{host}:{port}"
    async with websockets.connect(uri, ping_interval=120) as websocket:
        con_id = str(uuid4())
        await websocket.send(pickle.dumps({'type': 'CONN_INIT', 'data': con_id}))
        try:
            key = await websocket.recv()
            key = pickle.loads(key)
            pubkey = s.load_pem_public_key(key['data'])
            SERVER_CREDS['server_epbkey'] = pubkey
            print("RECEIVED SERVER PUBLIC KEY")
            await websocket.send(pickle.dumps({'type': 'CONN_ENCRYPT_C', 'data': CLIENT_CREDS['client_epbkey']}))
            print(en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey']))

        except websockets.exceptions.ConnectionClosedError as error:
            print("Disconnected from Server! Error:\n", error)
            exit()

        while True:
            try:
                await send_message(websocket, await cli.main_menu(SERVER_CREDS, CLIENT_CREDS, websocket, workingdir))
            except Exception as e:
                print("Disconnected from Server! Error:\n", e)
                exit()


SERVER_CREDS = {}
CLIENT_CREDS = {}

if __name__ == '__main__':
    client_eprkey, client_epbkey = en.create_rsa_key_pair()
    CLIENT_CREDS['client_eprkey'] = client_eprkey
    CLIENT_CREDS['client_epbkey'] = en.ser_key_pem(client_epbkey, 'public')
    try:
        rootdir = os.path.dirname(os.path.abspath(__file__))
        f = open(f'{rootdir}/config.yml', 'r+')
        yaml = loadyaml(f.read())
        if not yaml:
            f.close()
            os.remove(f'{rootdir}/config.yml')
            print(i18n.firstrun.empty_config, i18n.firstrun.exit, end='\n')
            exit()
        check_missing_config(f, yaml, 'working_directory')
        check_missing_config(f, yaml, 'homeserver_address')
        check_missing_config(f, yaml, 'homeserver_port')
        f.close()

    except FileNotFoundError as err:
        print(i18n.firstrun.config_not_found, i18n.firstrun.exec)
        execute_firstrun()

    workingdir = yaml['working_directory']
    CLIENT_CREDS['workingdir'] = workingdir
    host, port = yaml['homeserver_address'], yaml['homeserver_port']

    asyncio.run(main(host, port))
