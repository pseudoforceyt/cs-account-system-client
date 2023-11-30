import os, sys
from . import packet_handler as p
import asyncio
from i18n import demo

def cls():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


async def main_menu(SERVER_CREDS, CLIENT_CREDS, websocket, wdir):
    print("Account System Demonstration Frontend")
    print("Welcome!")
    print("Available Operations:")
    print("> signup\t(Sign up)")
    print("> login \t(Log in)")
    print("> auth  \t(Authenticate)")
    print("> logout\t(Logout)")
    print("> del\t(Delete)")
    print("> exit  \t(Exit)")
    while True:
        print("What would you like to do?")
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
                if input(demo.logout_p + ' (y/N) > ').lower() == 'y':
                    flag = await p.logout(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
                    return flag
                else:
                    print("Logout cancelled.")
            case 'del':
                cls()
                print("Are you sure? Account deletion is irreversible")
                c = input("(y/N) > ")
                if c.lower() == 'y':
                    flag = await p.delete(SERVER_CREDS, CLIENT_CREDS, websocket, wdir)
                    return flag
                else:
                    print("Account deletion cancelled.")
            case 'exit':
                print("Goodbye!")
                sys.exit()
            case other:
                print("Enter a valid operation.")
