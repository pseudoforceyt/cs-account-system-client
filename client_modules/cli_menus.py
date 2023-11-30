import os, sys
from . import packet_handler as p
import asyncio
from i18n import demo
from i18n import menu

def cls():
    # function return value is assigned to _ to prevent it from printing to the console
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


async def main_menu(SERVER_CREDS, CLIENT_CREDS, websocket, wdir):
    print(menu.the_menu)
    while True:
        print(menu.input_p)
        c = input("> ").lower()
        match c:
            case 'signup':
                cls()
                return await p.signup(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
            case 'login':
                cls()
                return await p.login(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
            case 'auth':
                cls()
                return await p.auth(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
            case 'logout':
                cls()
                if input(demo.logout_p + '\n(y/N) > ').lower() == 'y':
                    flag = await p.logout(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
                    return flag
                else:
                    print(demo.logout_cancel)
            case 'del':
                cls()
                print()
                c = input("(y/N) > ")
                if c.lower() == 'y':
                    flag = await p.delete(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
                    return flag
                else:
                    print()
            case 'exit':
                print(menu.exit_msg)
                sys.exit()
            case other:
                print(menu.invalid_op)
