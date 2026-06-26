from nicegui import ui, app
import asyncio
import socket
import sys
import hashlib
import getpass
import time

#RSA encryption ~w~
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

from heapq import merge

import base64
import json

# Encrypt
def rsa_encrypt(plaintext, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(plaintext.encode())
    return encrypted

# Decrypt
def rsa_decrypt(ciphertext, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted = cipher.decrypt(ciphertext)
    return decrypted.decode()

#AES stuff
def encrypt_AES_GCM(msg, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg.encode())
    blob = aesCipher.nonce + ciphertext + authTag
    return base64.b64encode(blob).decode('utf-8')
    #return (ciphertext, aesCipher.nonce, authTag)

def decrypt_AES_GCM(encryptedMsg, secretKey):
    #encryptedMsg = base64.b64encode(encryptedMsg)
    encryptedMsg = base64.b64decode(encryptedMsg.encode())
    nonce = encryptedMsg[:16]
    ciphertext = encryptedMsg[16:-16]
    authTag = encryptedMsg[-16:]

    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext

SERVER_IP = "127.0.0.1"
#SERVER_IP = '147.185.221.31'
SERVER_PORT = 2700
#SERVER_PORT = 46163
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('127.0.0.1', 27000))

transport = None

#obtaining the aes256 key#
skey = None

authenticating = False
authKey = None

keyWait = asyncio.Event()
keyWait.clear()

server_addr = None

async def resolve_server_addr():
    global SERVER_IP, SERVER_PORT
    if 'gl' in SERVER_IP:
        raise RuntimeError("Playit IP")
    loop = asyncio.get_running_loop()
    infos = await loop.getaddrinfo(SERVER_IP, SERVER_PORT, family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print(infos[0][4])
    return infos[0][4]

async def alt_resolve_server_addr():
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(
            SERVER_IP, SERVER_PORT, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP
        )
    except socket.gaierror as e:
        print(f"DNS resolution failed, {e}")
        return

    if not infos:
        print(f"No address info found")
        return

    # Pick the first resolved address
    family, type_, proto, canonname, sockaddr = infos[0]
    ip, resolved_port = sockaddr[0], sockaddr[1]
    print(ip,resolved_port)
    return (ip,resolved_port)

async def encrypt_connect():
    global authenticating, authKey, keyWait
    global skey
    authenticating = True

    #generate RSA keys

    key = RSA.generate(2048)
    pkey = key
    public_key = key.publickey()
    pub_key_str = key.publickey().export_key().decode('utf-8')

    msg1 = "Ÿ:"+pub_key_str
    transport.sendto(msg1.encode())

    await keyWait.wait()
    keyWait.clear()

    skey1 = rsa_decrypt(authKey, pkey)
    print(skey1)
    skey = skey1.encode()
    
    #stupid data races
    await asyncio.sleep(.5)
    authenticating = False
    



def uid_hash(uid,psw):
    combined = f"{uid}|owo-{psw}"
    hash_object = hashlib.sha384(combined.encode('utf-8'))
    return hash_object.hexdigest()

username, password = None, None
loadin = False
user_validated = False
stop_tasks = False
user_input = ''
pass_input = ''
sip1,spt1 = '',''
#running1= False

class UDP_Protocol(asyncio.DatagramProtocol):
    global authenticating, authKey, keyWait
    def __init__(self, on_datagram):
        self.on_datagram = on_datagram
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, address):
        global authenticating, authKey, keyWait
        #pass to auth thingy
        if authenticating:
            authKey = data
            keyWait.set()

        asyncio.create_task(self.on_datagram(data, address, self.transport))

messages =  [] #Message Tuple (find, author, content, timestamp)
smessages = []

async def submit_auth(user_input, pass_input):
    global username
    global password, skey
    global loadin
    global user_validated
    global running1, keyWait, authKey, authenticating, transport

    authenticating = True
    
    username = user_input.value.strip()
    password = pass_input.value.strip()

    print(username, password)
    print(type(username))

    payload = username+'|'+uid_hash(username, password)
    payload = encrypt_AES_GCM(payload, skey)
    payload = "ŸŸŸ:"+payload

    loadin = True
    transport.sendto(payload.encode())

    await keyWait.wait()
    data2 = authKey
    
    data2= data2.decode()
    if data2 == "v:pass":
        authenticating = False
        await asyncio.sleep(0.2)
        user_validated = True
        ui.navigate.to('/main')
        running1= True
    
        transport.sendto("ŸŸŸŸ:".encode())

    authenticating = False
#^^ figure out a better login and auth and server selection screen


async def submit_addr(spt1, sip1):
    global SERVER_IP
    global SERVER_PORT


    if not(spt1.value.strip() == '' and sip1.value.strip() == ''):
        SERVER_IP = spt1.value.strip()
        SERVER_PORT = spt1.value.strip()

async def recieve_messages(data, address, transport):
    global authenticating
    global messages, smessages
    if authenticating:
        print("still under auth, cancelling message read")
        return
    
    print('uwu')
    decode_data = data.decode(errors='ignore')

    try:
        decode_data_meta, decode_data_content = decode_data.split(":", 1)
    except:
        #should only happen due to programming skill issues
        print('unknown meta', decode_data)
        return

    if decode_data_meta.count("p") == 1:
        dcData = decrypt_AES_GCM(decode_data_content, skey)
        dJson = base64.b64decode(dcData).decode('utf-8')
        msgList = json.loads(dJson)

        #print(msgList, type(msgList), msgList[0])

        messages.extend(msgList)
        print(messages)

        display_messages.refresh()

    if decode_data_meta.count("n") == 1:
        print('pinged')

    if decode_data_meta.count("m") == 1:
        dcData = decrypt_AES_GCM(decode_data_content, skey)
        #debug
        print(dcData)
        securemode = False
        Mmeta, Mdata = dcData.decode().split(':',1)
        if '$' in Mmeta:
            securemode = True
            Mmeta.replace("$", '')

        cALen, cTime, cFind = Mmeta.split('-')
        cALen = int(cALen)
        cAuthor = Mdata[:cALen]
        cContent = Mdata[cALen:]

        if not securemode:
            messages.append((cFind, cAuthor, cContent, cTime))
        else:
            smessages.append((cFind, cAuthor, cContent, cTime))
            del cContent
            del dcData, Mdata
        
        display_messages.refresh()

    if decode_data_meta.count('v') >= 1:
        print(decode_data_content)
    


async def update_local_messages():    
    global messages, smessages
    #manage chat messages here
    #check test.py for heapq algorithm

    return list(merge(messages, smessages, key=lambda x:x[0]))
    
    


@ui.page('/')
def auth_page():
    global user_input
    global pass_input
    global loadin
    
    ui.label("Hiii :3 Welcome!").style('text-align: center; font-size: 300%; color: #7851A9').classes("w-full center")
    with ui.splitter(value=50).classes("w-full") as splitter:
        with splitter.before:
            uinput = ui.input(label = "Username ~w~",
                    placeholder = "enter your username",
            ).classes("w-3/4 mx-auto")
            pinput = ui.input(label = "Password Please :3",
                            password = True,
                            password_toggle_button= True,
                            placeholder = 'enter your password'
            ).classes('w-3/4 mx-auto')

            ui.button('Submit',
                    on_click=lambda: submit_auth(uinput, pinput)
            ).classes('w-3/4 mx-auto')
        with splitter.after:
            sip_input = ui.input(label = "Server IP",
                                 placeholder="Leave blank for default ~w~"
            ).classes('w-3/4 mx-auto')
            spt_input = ui.input(label = "Server Port",
                                 placeholder="Also leave blank for default"
            ).classes('w-3/4 mx-auto')
            ui.button("Submit Address",
                      on_click=lambda:submit_addr(spt_input, sip_input)
            ).classes('w-3/4 mx-auto')

@ui.refreshable
async def display_messages():
    #call update_local_messages and await it to get the content to display
    displayData = await update_local_messages()
    print('\n',displayData)

    #Message Tuple (find, author, content, timestamp)
    with ui.scroll_area().classes('w-full h-full'):
        for msg in displayData:

            ui.chat_message(
                text=msg[2],
                name=msg[1],
                stamp=msg[3]
            )

async def sendMessage(content, secureStatus):
    global transport
    if secureStatus:
        scontent = encrypt_AES_GCM(content,skey)
        scontent = "ŸŸ$:"+scontent
    else:
        scontent = encrypt_AES_GCM(content, skey)
        scontent = "ŸŸ:"+scontent

    print(scontent)
    transport.sendto(scontent.encode())

@ui.page('/main')
async def main_page():
    with ui.splitter(horizontal=True, limits=(9,9), value=9).classes("w-full h-[calc(100vh-2rem)]") as splitter:
        with splitter.before:
            ui.label("27's Server").style('text-align: center; font-size: 350%; color: #7851A9').classes("w-full center")
        with splitter.after:
            with ui.grid(rows='17fr 3fr').classes('h-full w-full'):
                await display_messages()
                
                with ui.row().classes('w-full'):
                    user_TextInput = ui.textarea(label='Enter Message')
                    secureSwitch = ui.switch("Secure Message", value=False)
                    ui.button('Send', on_click=lambda: sendMessage(user_TextInput.value, secureSwitch.value))



'''@ui.page('/main')
async def main_page():
    with ui.grid(rows="10% 80% 10%").classes('w-full h-full gap-0'):
        ui.label("27's Server").style('text-align: center; font-size: 350%; color: #7851A9').classes("w-full center")

        await display_messages()

        ui.label('uwu')'''

#use ui.scroll_area() and chat messages!


async def debug1():
    x=1
    while x<500:
        x+=1
        print(x)
        await asyncio.sleep(1)

async def UDP_Reciever():
    global SERVER_IP, SERVER_PORT, sock, transport
    global server_addr
    loop = asyncio.get_running_loop()

    try:
        server_addr = await resolve_server_addr()
    except:
        print("performing alternate address resolver")
        server_addr = await alt_resolve_server_addr()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDP_Protocol(recieve_messages), local_addr=('0.0.0.0', 27000), remote_addr=server_addr)


    await encrypt_connect()
    print("Reciever up")

    try: 
        await asyncio.Future()
    finally:
        transport.close()


async def on_startup():
    asyncio.create_task(UDP_Reciever())


async def on_shutdown():
    global smessages, skey
    smessages, skey = None, None
    global stop_tasks
    stop_tasks = True


app.on_startup(on_startup)
app.on_shutdown(on_shutdown)

ui.run(dark = True)