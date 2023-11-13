import asyncio
import websockets
import pickle
import os
from . import encryption as en
from getpass import getpass
from yaml import load as loadyaml

sig_map = {
    'CONN_OK':"Connection to the server was successful",
    'CAPTCHA_WRONG':"The CAPTCHA code you entered was wrong. Try performing the action again",
    'SIGNUP_OK':"The account was successfully created",
    'SIGNUP_MISSING_CREDS': '',
    'SIGNUP_MISSING_CREDS': '',
    'SIGNUP_USERNAME_ABOVE_LIMIT': '',
    'SIGNUP_USERNAME_ALREADY_EXISTS': '',
    'SIGNUP_EMAIL_ABOVE_LIMIT': '',
    'SIGNUP_NAME_ABOVE_LIMIT': '',
    'SIGNUP_DOB_INVALID': '',
    'SIGNUP_PASSWORD_ABOVE_LIMIT': '',
    'SIGNUP_ERR': '',
    'LOGIN_MISSING_CREDS': '',
    'LOGIN_INCORRECT_PASSWORD': '',
    'LOGIN_ACCOUNT_NOT_FOUND': '',
    'LOGIN_OK': '',
    'QUEUE_END': '',
    'TOKEN_EXPIRED': '',
    'TOKEN_INVALID': '',
    'CHAT_PUBKEY_MISSING': '',
    'CHAT_PUBKEY_INVALID': '',
    'CHAT_PUBKEY_OK': '',
    'ROOM_DNE': '',
    'MKROOM_INSUFFICIENT_PARTICIPANTS': '',
    'MKROOM_NOT_IMPLEMENTED': '',
    'MKROOM_OK': '',
    'SENT': '',
    'MSG_NOT_YOURS': ''
}

async def status(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    if data['sig'] == 'CHAT_PUBKEY_MISSING':
        await send_pubkey(SERVER_CREDS, CLIENT_CREDS, websocket)
    print(sig_map[data['sig']])

async def captcha(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    with open('captcha.png','wb') as f:
        f.write(data['challenge'])
    print("Open the captcha.png in the client folder and enter the digits here:")
    solved = int(input("> "))
    solved_packet = pickle.dumps({'type':'S_CAPTCHA', 'data':{'solved':solved}})
    outpacket = en.encrypt_data(solved_packet, SERVER_CREDS['server_epbkey'])
    await websocket.send(outpacket)
    return en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])

async def send_pubkey(SERVER_CREDS, CLIENT_CREDS, websocket):
    rootdir = os.path.dirname(os.path.abspath(__file__))
    f = open(f'{rootdir}/config.yml', 'r+')
    yaml = loadyaml(f.read())


def signup(SERVER_CREDS, CLIENT_CREDS, websocket, de_p):
    data = {}
    data['user'] = input("Enter your username: ")
    data['email'] = input("Enter your email: ")
    data['fullname'] = input("Enter your full name: ")
    data['dob'] = input("Enter your date of birth (YYYY-MM-DD or DD-MM-YYYY): ")
    pwd = getpass("Enter your password: ")
    if pwd == getpass("Confirm your password: "):
        data['password'] = pwd
    else:
        return 'ERR_CONFIRM'
    return en.encrypt_data({'type':'SIGNUP', 'data':data}, SERVER_CREDS['server_epbkey'])
    
def login(SERVER_CREDS, CLIENT_CREDS, websocket, de_p):
    # {'type':'LOGIN', 'data':{'id':username/email,'password':password,'save':True or False}}
    data = {}
    data['id'] = input("Enter username/email: ")
    data['password'] = getpass("Enter your password: ")
    if input("Save login? No need to re-login for 30 days (y/N)").lower() == 'y':
        data['save'] = True
    else:
        data['save'] = False
    return en.encrypt_data({'type':'LOGIN', 'data':data}, SERVER_CREDS['server_epbkey'])



packet_map = {
    'STATUS':status,
    'CAPTCHA':captcha,
#    'TOKEN_GEN':save_token,

}   
async def handle(SERVER_CREDS, CLIENT_CREDS, websocket, de_packet):
    type = de_packet['type']
    data = de_packet['data']

    if type in packet_map.keys():
        func = packet_map[type]
        return await func(SERVER_CREDS, CLIENT_CREDS, websocket, data)

async def dispatch(SERVER_CREDS, CLIENT_CREDS, websocket, de_packet):
    type = de_packet['type']
    data = de_packet['data']

    if type in packet_map.keys():
        func = packet_map[type]
        await websocket.send(await func(SERVER_CREDS, CLIENT_CREDS, websocket, data))