import asyncio
import websockets
import pickle
import os
from . import encryption as en
from getpass import getpass
from yaml import load as loadyaml
from i18n import sig_map, demo, log


async def status(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    print(sig_map[data['sig']])


async def captcha(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    with open('captcha.png', 'wb') as f:
        f.write(data['challenge'])
    print(demo.captcha_p)
    solved = int(input("> "))
    solved_packet = {'type': 'S_CAPTCHA', 'data': {'solved': solved}}
    await websocket.send(en.encrypt_data(solved_packet, SERVER_CREDS['server_epbkey']))
    resp = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
    if resp['type'] == 'STATUS':
        return resp['data']['sig']
    else:
        return resp


async def signup(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    data = {}
    data['user'] = input(demo.user_p)
    data['email'] = input(demo.email_p)
    data['fullname'] = input(demo.name_p)
    data['dob'] = input(demo.dob_p.format("(YYYY-MM-DD or DD-MM-YYYY)"))
    while True:
        pwd = getpass(demo.pass_p)
        conf = getpass(demo.pass_confirm)
        if pwd == conf:
            data['password'] = pwd
            break
        else:
            print(demo.pass_mismatch)
    await websocket.send(en.encrypt_data({'type': 'SIGNUP', 'data': data}, SERVER_CREDS['server_epbkey']))
    captcha_prompt = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
    captcha_flag = await captcha(SERVER_CREDS, CLIENT_CREDS, websocket, captcha_prompt['data'])
    if captcha_flag == 'SIGNUP_OK':
        print(demo.signup_success)
    else:
        print(demo.error_i, sig_map[captcha_flag])


async def login(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    # {'type':'LOGIN', 'data':{'id':username/email,'password':password,'save':True or False}}
    data = {'id': input(demo.id_p), 'password': getpass(demo.pass_p)}
    if input(demo.save_p + ' (y/N) > ').lower() == 'y':
        data['save'] = True
    else:
        data['save'] = False
    await websocket.send(en.encrypt_data({'type': 'LOGIN', 'data': data}, SERVER_CREDS['server_epbkey']))
    captcha_prompt = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
    captcha_flag = await captcha(SERVER_CREDS, CLIENT_CREDS, websocket, captcha_prompt['data'])
    if isinstance(captcha_flag, str):
        print(captcha_flag + ":", sig_map[captcha_flag])
    else:
        await save_token(SERVER_CREDS, CLIENT_CREDS, websocket, captcha_flag)


async def save_token(SERVER_CREDS, CLIENT_CREDS, websocket, de_p):
    # {'type':'TOKEN_GEN','data':{'token':access_token}}
    dir = CLIENT_CREDS['workingdir']
    try:
        with open(dir + '/creds/acc_token', 'w') as f:
            f.write(de_p['data']['token'])
        print(demo.token_got)
    except Exception as ee:
        print(demo.token_fail.format(ee))


async def auth(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    user = input(demo.id_p)
    try:
        with open(dir + '/creds/acc_token', 'r') as f:
            token = f.read().rstrip('\r\n')
            if token:
                await websocket.send(en.encrypt_data({'type': 'AUTH_TOKEN', 'data': {'user': user, 'token': token}},
                                                     SERVER_CREDS['server_epbkey']))
            elif not token:
                print(demo.token_nf)
                return None
            flag = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
            if flag['data']['sig'] == 'LOGIN_OK':
                print(demo.end)
            else:
                print(flag['data']['sig'] + ":", sig_map[flag['data']['sig']])

    except Exception as ee:
        print(demo.auth_err.format(ee))


async def logout(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    if input(demo.logout_p + ' (y/N) > ').lower() == 'y':
        await websocket.send(en.encrypt_data({'type': 'LOGOUT', 'data': {}}, SERVER_CREDS['server_epbkey']))
        flag = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
        match flag['data']['sig']:
            case 'LOGOUT_OK':
                print(demo.logout_success)
            case other:
                print(flag['data']['sig'] + ":", sig_map[flag['data']['sig']])
    else:
        print("Cancelled logout.")


packet_map = {
    'STATUS': status,
    'CAPTCHA': captcha,
    'TOKEN_GEN': save_token
}


async def handle(SERVER_CREDS, CLIENT_CREDS, websocket, de_packet):
    type = de_packet['type']
    data = de_packet['data']
    print(log.tags.debug + log.handle_packet.format(type))
    if type in packet_map.keys():
        func = packet_map[type]
        return await func(SERVER_CREDS, CLIENT_CREDS, websocket, data)
