import asyncio
import websockets
import pickle
from . import encryption as en

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
    print(sig_map[data['sig']])

async def captcha(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    with open('captcha.png','wb') as f:
        f.write(data['challenge'])
    print("Open the captcha.png in the client folder and enter the digits here:")
    solved = int(input("> "))
    solved_packet = pickle.dumps({'type':'S_CAPTCHA', 'data':{'solved':solved}})
    outpacket = en.encrypt_packet(solved_packet, SERVER_CREDS['server_epbkey'])
    await websocket.send(outpacket)
    return en.decrypt_packet(await websocket.recv(), CLIENT_CREDS['client_eprkey'])

async def signup(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    

packet_map = {
    'STATUS':status,
    'CAPTCHA':captcha,
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