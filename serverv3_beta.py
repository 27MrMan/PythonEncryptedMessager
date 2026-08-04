import socket
import pandas
import sys, os, shutil
import datetime
import asyncio

#database for storing messages OwO
#import sqlite3
import aiosqlite

#RSA encryption >///<
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import string, secrets
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

import base64
import json

#conn = sqlite3.connect('messages.db')
#cursor = conn.cursor()

conn = None
async def start_aiosqlite():
    global conn, current_message_indexes
    conn = await aiosqlite.connect('messages.db')
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        FIND INTEGER PRIMARY KEY NOT NULL,
        AUTHOR TEXT NOT NULL,
        CONTENT TEXT NOT NULL,
        TIMESTAMP TEXT NOT NULL
    )
    ''')
    await conn.commit()

    global S_conn
    S_conn = await aiosqlite.connect(":memory:")
    await S_conn.execute('''
    CREATE TABLE IF NOT EXISTS s_messages (
        FIND INTEGER PRIMARY KEY NOT NULL,
        AUTHOR TEXT NOT NULL,
        CONTENT TEXT NOT NULL,
        TIMESTAMP TEXT NOT NULL
    )
    ''')
    await S_conn.commit()

    tcsr = await conn.cursor()
    stcsr = await S_conn.cursor()

    await tcsr.execute('SELECT EXISTS(SELECT 1 FROM messages LIMIT 1)')
    connvals = await tcsr.fetchall()
    if connvals[0][0] == 0:
        await tcsr.execute('INSERT INTO messages (FIND, AUTHOR, CONTENT, TIMESTAMP) VALUES (1, "server", "init_database", ?)', (datetime.datetime.now(datetime.UTC).timestamp(),))
        await conn.commit()

    await stcsr.execute('SELECT EXISTS(SELECT 1 FROM s_messages LIMIT 1)')
    sconnvals = await stcsr.fetchall()
    if sconnvals[0][0] == 0:
        await stcsr.execute('INSERT INTO s_messages (FIND, AUTHOR, CONTENT, TIMESTAMP) VALUES (1, "server", "init_database", ?)', (datetime.datetime.now(datetime.UTC).timestamp(),))
        await S_conn.commit()

    await tcsr.execute("SELECT * FROM messages ORDER BY FIND DESC LIMIT 1")
    cindex = await tcsr.fetchone()
    await stcsr.execute('SELECT * FROM s_messages ORDER BY FIND DESC LIMIT 1')
    dindex = await stcsr.fetchone()

    current_message_indexes = [cindex[0], dindex[0]]

    print('current message counts:', current_message_indexes)

    await tcsr.close()
    await stcsr.close()

    if not(os.path.exists('users.csv')):
        shutil.copy('templates/users.csv', 'users.csv')
    if not(os.path.exists('users_adder.csv')):
        shutil.copy('templates/users_adder.csv', 'users_adder.csv')


#i did the thing, finally

#SQlite code



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

#key used to show messages to server: Ÿ
spec_key = 'Ÿ'

#AES stuff
#iteration 1 in client code
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


IP = "127.0.0.1" 
#port can be modified
PORT = 2700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Listening for clients at {(IP, PORT)}")


user_keyList = {}
user_authorList = {}
decode_data = None

current_message_indexes = None


write_lock = asyncio.Lock()
register_dataframe_lock = asyncio.Lock()

async def handle_message(data, address, conn, transport, S_conn):
    # conn and transport are passed explicitly
    usingcursor = False
    usingscursor = False

    # globals still in use for other state
    global user_keyList, user_authorList
    global IP, PORT
    global current_message_indexes


    decode_data = data.decode(errors='ignore')

    if address not in user_keyList.keys():
        user_keyList[address] = ""
    

    #*i forgot modified clients can exist :sob:*use a special character, and str.split() at the first occurance!
    try:
        decode_data_meta, decode_data_content = decode_data.split(":", 1)
    except:
        print('\nno meta?',decode_data)
        return

    match decode_data_meta.count("Ÿ"):
        case 1: #get AES key
            print('authenticating a client')
            charset = string.ascii_letters + string.digits + string.punctuation
            temp_skey = secrets.token_urlsafe(32)[:32]

            user_keyList[address] = temp_skey
            temp_ekey = rsa_encrypt(temp_skey, RSA.import_key(decode_data_content))
            
            transport.sendto(temp_ekey, address)

        case 2: #recieve message
            if address not in user_authorList.keys():
                print("i smell a modified client","\nRico: Kaboom...?")
                return


            temp_msg = decrypt_AES_GCM(decode_data_content, user_keyList[address].encode())
            temp_msg = temp_msg.decode()
            
            #structure: index, author, content, timestamp

            if decode_data_meta.count("$")==1:
                scursor = await S_conn.cursor()
                usingscursor = True


                cauthor = user_authorList[address]
                ccontent = temp_msg.strip()
                ctime = datetime.datetime.now(datetime.UTC).timestamp()

                try:
                    async with write_lock:
                        cindex = int(current_message_indexes[1])+1
                        current_message_indexes[1]+=1
                        await scursor.execute("INSERT INTO s_messages (FIND, AUTHOR, CONTENT, TIMESTAMP) VALUES (?, ?, ?, ?)",
                                    (cindex, cauthor, ccontent, ctime))
                        await S_conn.commit()
                except Exception as e:
                    print("SQL PROBLEM!!", e)
                
                #print("SECURE message recieved", cauthor)
        
            else:
                cursor = await conn.cursor()
                usingcursor = True     


                cauthor = user_authorList[address]
                ccontent = temp_msg.strip()
                ctime = datetime.datetime.now(datetime.UTC).timestamp()

                try:
                    async with write_lock:
                        cindex = int(current_message_indexes[0])+1
                        current_message_indexes[0]+=1
                        await cursor.execute("INSERT INTO messages (FIND, AUTHOR, CONTENT, TIMESTAMP) VALUES (?, ?, ?, ?)",
                                    (cindex, cauthor, ccontent, ctime))
                        await conn.commit()
                except Exception as e:
                    print("SQL PROBLEM!!",e)

                #print("message recieved", cauthor)

            #once again, theres a better way to do this isnt there
            cMG = str(len(cauthor))+'-' + str(ctime)+'-'+str(cindex)+':'+cauthor+ccontent
            for ad in user_authorList.keys():
                v1 = encrypt_AES_GCM(cMG, user_keyList[ad].encode())
                if usingscursor:
                    v1='m$:'+v1
                else:
                    v1='m:'+v1
                transport.sendto(v1.encode(), ad)

        case 3: #login
            #print(cleaned_data)
            dcList = decrypt_AES_GCM(decode_data_content, user_keyList[address].encode())
            inputlist = dcList.decode().strip().split("|")
            user_collection = pandas.read_csv('users.csv')
            #^feature to allow change in user list without restarting server :3


            if not(inputlist[0] in user_collection['userid'].tolist()):
                transport.sendto("v:User not found".encode(), address)
                print(f"goofy ahh user {inputlist[0]} tried joinin' ")
                return
            
            passhash_lookup = user_collection.loc[user_collection['userid'] == inputlist[0], 'password'].item()
            if inputlist[1] == passhash_lookup:
                transport.sendto("v:pass".encode(), address)
                
                print(inputlist[0], 'has joined')
                user_authorList[address] = inputlist[0]

        case 4: #client request messages
            print(f"Client {address}, requested messages")
            
            if address not in user_authorList.keys():
                print("Possible attack!")
                return

            cursor = await conn.cursor()
            usingcursor = True

            bufsize = 50

            await cursor.execute('SELECT * FROM messages WHERE FIND > ?', (current_message_indexes[0]-bufsize,))
            msgsContent = await cursor.fetchall()
            #order by timestamp, send only bufsize (50 ig) messages using between

            jBytes = json.dumps(msgsContent).encode('utf-8')
            enc_b64 = base64.b64encode(jBytes).decode('utf-8')
            msgList = encrypt_AES_GCM(enc_b64, user_keyList[address].encode())
            msgList = 'p:'+msgList


            transport.sendto(msgList.encode(), address)

        case 5: #client ping
            print(f"client {address}, pinged")

            transport.sendto("n:Ping Recieved".encode(), address)

        case 6: #adding new users
            uCredContent = decrypt_AES_GCM(decode_data_content, user_keyList[address].encode()).decode()
            if uCredContent.count('|')>1:
                print('invalid registration username')
                return
            
            currentUsers = pandas.read_csv('users.csv')
            currentRegUsers = pandas.read_csv('users_adder.csv')

            rUser, rPass = uCredContent.split('|')
            
            if rUser in currentUsers['userid'].tolist():
                print(f"User {rUser} already exists! Registration cancelled")
                return
            if rUser in currentRegUsers['userid'].tolist():
                print(f'User {rUser} in registration queue attempted re-registering')
                return

            if rUser.replace('-','').replace('_','').isalnum() and rPass.isalnum():
                tDf = {'userid':[rUser], 'password':[rPass]}
                aDf = pandas.DataFrame(tDf)

                try:
                    async with register_dataframe_lock:
                        aDf.to_csv('users_adder.csv', mode='a', index=False, header=False)
                    print('a user wants to register! run user_adder.py sometime')

                except Exception as e:
                    print(f"user registration error csv {e}!")

        case 7:
            print(f'user {user_authorList[address]} at {address} has hit the killswitch!')
            del user_authorList[address], user_keyList[address]

    if usingcursor:
        await cursor.close()
    if usingscursor:
        await scursor.close()

class UDP_Protocol(asyncio.DatagramProtocol):
    def __init__(self, on_datagram, conn, S_conn):
        self.on_datagram = on_datagram
        self.conn = conn
        self.S_conn = S_conn
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, address):
        #Called automatically when a UDP packet is received.
        message = data.decode()
        #print(f"Received {message!r} from {address}")
        
        # Run the callback asynchronously, passing the shared connection and transport
        asyncio.create_task(self.on_datagram(data, address, self.conn, self.transport, self.S_conn))

async def main():
    await start_aiosqlite()
    loop = asyncio.get_running_loop()

    # create a protocol instance that closes over the sqlite connections
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDP_Protocol(handle_message, conn, S_conn),
        local_addr=('0.0.0.0', PORT)
    )
    print(f"New Server Running on 0.0.0.0:{PORT}")

    try:
        #await asyncio.sleep(3600)
        await asyncio.Future()
    finally:
        transport.close()

asyncio.run(main())
