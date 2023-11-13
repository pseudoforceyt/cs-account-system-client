import asyncio
import websockets
import os
from cryptography.hazmat.primitives import serialization as s
from client_modules import encryption as en
from client_modules import packet_handler as p
from client_modules import db_handler as db
from client_modules import first_run
from uuid import uuid4
import i18n
from yaml import safe_load as loadyaml
from yaml import dump as dumpyaml
import pickle
from sys import exit

async def send_message(websocket, message):
    outpacket = en.encrypt_data(
        message, SERVER_CREDS['server_epbkey']
    )
    await websocket.send(outpacket)
    response = await websocket.recv()
    return await recv_message(websocket, response)

async def handle_resp(websocket, response):
    inpacket = en.decrypt_data(response, CLIENT_CREDS['client_eprkey'])
    print(inpacket)
    handled = await p.handle(SERVER_CREDS, CLIENT_CREDS, websocket, inpacket) # handle here using type and data
    print('resposne handaled')
    return handled

async def recv_message(websocket, message):
    inpacket = en.decrypt_data(message, CLIENT_CREDS['client_eprkey'])
    # handle check
    await p.handle(SERVER_CREDS, CLIENT_CREDS, websocket, inpacket)

def execute_firstrun():
    first_run.main()
    print(i18n.firstrun.security)
    db.decrypt_creds(en.fermat_gen(first_run.working_dir.workingdir), first_run.working_dir.workingdir)
    print(i18n.firstrun.initialize_db)
    db.initialize_schemas()
    db.close()
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
    async with websockets.connect(uri, ping_interval=30) as websocket:
        con_id = str(uuid4())
        await websocket.send(pickle.dumps({'type':'CONN_INIT', 'data':con_id}))
        try:
            key = await websocket.recv()
            key = pickle.loads(key)
            pubkey = s.load_pem_public_key(key['data'])
            SERVER_CREDS['server_epbkey'] = pubkey
            print("RECEIVED SERVER PUBLIC KEY")
            await websocket.send(pickle.dumps({'type':'CONN_ENCRYPT_C','data':CLIENT_CREDS['client_epbkey']}))
            print(en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey']))

        except websockets.exceptions.ConnectionClosedError as err:
            print("Disconected from Server! Error:\n",err)
            exit()
        
        while True:
            try:
                await asyncio.gather(
                    send_message(websocket),
                    recv_message(websocket, await websocket.recv()),
                )
            except Exception as eroa:
                print("Disconected from Server! Error:\n",eroa)
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
    host, port = yaml['homeserver_address'], yaml['homeserver_port']

    try:
        fkey = en.fermat_gen(workingdir)
        db.decrypt_creds(fkey, workingdir)
    except Exception as w:
        print("Error while decrypting database credentials. Check your password\n", w)
        print(i18n.firstrun.exit)
        exit()

    try:
        with open(f'{workingdir}/creds/chat_publickey', 'rb') as f:
            pem_pubkey = f.read()
            pubkey = en.deser_pem(pem_pubkey, 'public')
    except FileNotFoundError:
        print("Could not find chat encryption public key. Client will now generate it from the private key.")
        try:
            with open(f'{workingdir}/creds/chat_privatekey', 'rb') as f:
                en_pem_prkey = f.read()
            pem_prkey = fkey.decrypt(en_pem_prkey)
            prkey = en.deser_pem(pem_prkey, 'private')
            pubkey = prkey.public_key()

            with open(f'{workingdir}/creds/chat_publickey', 'wb') as f:
                f.write(pem_pubkey)
        except FileNotFoundError:
            print("Could not find chat encryption keypair. Client will now generate it again.")
            ch = input("THIS OPERATION IS NOT SUPPORTED YET. Continue? (y/n) > ")
            if ch.lower() == 'y':
                db.clear_queue(user=None)
                first_run.save_chat_keypair(fkey, workingdir)
                print(i18n.firstrun.exit)
                exit()
            if ch.lower() == 'n':
                print("Key ah kaanume enna panradhu ippo?")
                exit()
    else:
        with open(f'{workingdir}/creds/chat_privatekey', 'rb') as f:
            en_pem_prkey = f.read()
            pem_prkey = fkey.decrypt(en_pem_prkey)
            prkey = en.deser_pem(pem_prkey, 'private')

    asyncio.get_event_loop().run_until_complete(main(host,port))
    asyncio.get_event_loop().run_forever()

"""
import asyncio
import websockets

# Main function to connect to the server and start the message handlers
async def main():
    async with websockets.connect(uri) as websocket:
        # Start the message handlers
        await asyncio.gather(
            handle_incoming_messages(websocket),
            handle_outgoing_messages(websocket),
        )

# Run the main function
asyncio.run(main())
"""