import asyncio
import websockets
import pickle
from . import encryption as en

sig_map = {
    'CONN_OK':"Connection to the server was successful",
    'CAPTCHA_WRONG':"The CAPTCHA code you entered was wrong. Try signing up again",
    'SIGNUP_OK':"The account was successfully created"
}

async def status(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    sig = data['sig']
    print(sig_map[sig])

async def captcha(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    with open('captcha.png','wb') as f:
        f.write(data['challenge'])
    print("Open the captcha.png in the client folder and enter the digites here:")
    solved = int(input("> "))
    solved_packet = pickle.dumps({'type':'S_CAPTCHA', 'data':{'solved':solved}})
    outpacket = en.encrypt_packet(solved_packet, SERVER_CREDS['server_epbkey'])
    await websocket.send(outpacket)
    return en.decrypt_packet(await websocket.recv(), CLIENT_CREDS['client_eprkey'])

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
