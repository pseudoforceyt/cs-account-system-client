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
    'TOKEN_EXPIRED': '',
    'TOKEN_INVALID': '',
    'LOGOUT_ERR': '',
    'NOT_LOGGED_IN': 'You need to be logged in to do that!',
    'TOKEN_NOT_FOUND': 'The provided auth token does not exist on the server. Log in again',
    'ACCOUNT_DNE': 'No such account found. Check your username/email'
}

async def status(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    print(sig_map[data['sig']])

async def captcha(SERVER_CREDS, CLIENT_CREDS, websocket, data):
    with open('captcha.png','wb') as f:
        f.write(data['challenge'])
    print("Open the captcha.png in the client folder and enter the digits here:")
    solved = int(input("> "))
    solved_packet = {'type':'S_CAPTCHA', 'data':{'solved':solved}}
    await websocket.send(en.encrypt_data(solved_packet, SERVER_CREDS['server_epbkey']))
    resp = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
    if resp['type'] == 'STATUS':
        return resp['data']['sig']
    else:
        return resp

async def signup(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    data = {}
    data['user'] = input("Enter your username: ")
    data['email'] = input("Enter your email: ")
    data['fullname'] = input("Enter your full name: ")
    data['dob'] = input("Enter your date of birth (YYYY-MM-DD or DD-MM-YYYY): ")
    while True:
        pwd = getpass("Enter your password: ")
        conf = getpass("Confirm your password: ")
        if pwd == conf:
            data['password'] = pwd
            break
        else:
            print("Passwords don't match. Try again")
    await websocket.send(en.encrypt_data({'type':'SIGNUP', 'data':data}, SERVER_CREDS['server_epbkey']))
    captcha_prompt = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
    captcha_flag = await captcha(SERVER_CREDS, CLIENT_CREDS, websocket, captcha_prompt['data'])
    if captcha_flag == 'SIGNUP_OK':
        print("Signup complete! Login with your credentials.")
    else:
        print("An error occurred:", sig_map[captcha_flag])
    
async def login(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    # {'type':'LOGIN', 'data':{'id':username/email,'password':password,'save':True or False}}
    data = {}
    data['id'] = input("Enter username/email: ")
    data['password'] = getpass("Enter your password: ")
    if input("Save login? No need to re-login for 30 days (y/N)").lower() == 'y':
        data['save'] = True
    else:
        data['save'] = False
    await websocket.send(en.encrypt_data({'type':'LOGIN', 'data':data}, SERVER_CREDS['server_epbkey']))
    captcha_prompt = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
    captcha_flag = await captcha(SERVER_CREDS, CLIENT_CREDS, websocket, captcha_prompt['data'])
    if isinstance(captcha_flag, str):
        print(captcha_flag+":", sig_map[captcha_flag])
    else:
        await save_token(SERVER_CREDS, CLIENT_CREDS, websocket, captcha_flag)

async def save_token(SERVER_CREDS, CLIENT_CREDS, websocket, de_p):
    # {'type':'TOKEN_GEN','data':{'token':access_token}}
    dir = CLIENT_CREDS['workingdir']
    try:
        with open(dir+'/creds/acc_token', 'w') as f:
            f.write(de_p['data']['token'])
        print("Successfully acquired token.")
    except Exception as ee:
        print("Token generation failed. Please try again. Error:")
        print(ee)

async def auth(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    user = input("Enter username/email: ")
    try:
        with open(dir+'/creds/acc_token', 'r') as f:
            token = f.read().rstrip('\r\n')
            if token:
                await websocket.send(en.encrypt_data({'type':'AUTH_TOKEN','data':{'user':user,'token':token}}, SERVER_CREDS['server_epbkey']))
            elif not token:
                print("You have to login first! Token not found.")
                return None
            flag = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
            if flag['data']['sig'] == 'LOGIN_OK':
                print("You have been logged in successfully.\nYour session is now active and this concludes the demonstration.\nIf you exit the app and decide to login again, you can use > auth to do it.")
            else:
                print(flag['data']['sig']+":", sig_map[flag['data']['sig']])

    except Exception as ee:
        print("Token authentication failed. Please login again. Error:")
        print(ee)

async def logout(SERVER_CREDS, CLIENT_CREDS, websocket, dir):
    if input("Are you sure you want to log out?\nThis will reset your token and you will have to login again.").lower() == 'y':
        await websocket.send(en.encrypt_data({'type':'LOGOUT', 'data':{}}, SERVER_CREDS['server_epbkey']))
        flag = en.decrypt_data(await websocket.recv(), CLIENT_CREDS['client_eprkey'])
        match flag['data']['sig']:
            case 'LOGOUT_OK':
                print("Successfully logged out. Token has been reset")
            case other:
                print(flag['data']['sig']+":", sig_map[flag['data']['sig']])
    else:
        print("Cancelled logout.")

packet_map = {
    'STATUS':status,
    'CAPTCHA':captcha,
    'TOKEN_GEN':save_token
}   
async def handle(SERVER_CREDS, CLIENT_CREDS, websocket, de_packet):
    type = de_packet['type']
    data = de_packet['data']
    print("HANDLING PACKET", type)
    if type in packet_map.keys():
        func = packet_map[type]
        return await func(SERVER_CREDS, CLIENT_CREDS, websocket, data)