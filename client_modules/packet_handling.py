import asyncio
import websockets


sig_map = {
    'CONN_OK':"Connection to the server was successful",
    'CAPTCHA_WRONG':"The CAPTCHA code you entered was wrong. Try signing up again",
    'SIGNUP_OK':"The account was successfully created"
}
async def status(data):
    sig = data['sig']
    print(sig_map[sig])
    