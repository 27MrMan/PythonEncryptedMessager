import socket
import pandas
import sys, os
import datetime
import asyncio

#database for storing messages OwO
import sqlite3

#RSA encryption >///<
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import string, secrets
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64

conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

#SQlite code

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        FIND INTEGER PRIMARY KEY NOT NULL,
        AUTHOR TEXT NOT NULL,
        CONTENT TEXT NOT NULL,
        TIMESTAMP TEXT NOT NULL
    )
''')



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
PORT = 2700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"Listening for clients at {(IP, PORT)}")


user_keyList = {}
user_authorList = {}
decode_data = None

#msg_pipeline = []
'''
async def addMsg():
    global conn, cursor
    global msg_pipeline
    
    while True:
        #make smaller for servers with more chatters
        await asyncio.sleep(.1) #time between each processed message

        if any(msg_pipeline):
            cindex, cauthor, ccontent, ctime = msg_pipeline[0]
            cursor.execute(f"INSERT INTO messages (FIND, AUTHOR, CONTENT, TIMESTAMP) VALUES ({cindex}, '{cauthor}', '{ccontent}', '{ctime}')")
            conn.commit()
            msg_pipeline = msg_pipeline [1:]
'''
#asyncio.run(addMsg())

async def handle_message(data, address):

    global user_keyList, user_authorList
    global conn, cursor
    global IP, PORT, sock

    decode_data = data.decode(errors='ignore')
    cleaned_data = decode_data.replace('Ÿ', '')
    #print(data, decode_data, cleaned_data, sep='\n')

    if address not in user_keyList.keys():
        user_keyList[address] = ""
    
    match decode_data.count("Ÿ"):
        case 1: #get AES key
            charset = string.ascii_letters + string.digits + string.punctuation
            temp_skey = secrets.token_urlsafe(32)[:32]
            #temp_skey = os.urandom(32)

            #DEBUG
            #print(temp_skey)

            user_keyList[address] = temp_skey
            temp_ekey = rsa_encrypt(temp_skey, RSA.import_key(cleaned_data))
            
            sock.sendto(temp_ekey, address)

        case 2: #recieve message
            if address not in user_authorList.keys():
                print("i smell a modified client","\nRico: Kaboom...?")
                return

            temp_msg = decrypt_AES_GCM(cleaned_data, user_keyList[address].encode())
            temp_msg = temp_msg.decode()


            #structure: index, author, content, timestamp
            indexfinder = cursor.execute(f"SELECT * FROM messages ORDER BY FIND DESC LIMIT 1")
            cindex = cursor.fetchone()
            #For initilizing an empty database, i have to add some code later
            cindex = int(cindex[0]) +1
            cauthor = user_authorList[address]
            ccontent = temp_msg.strip()
            ctime = datetime.datetime.now(datetime.UTC).timestamp()

            #msg_pipeline.append([cindex, cauthor, ccontent, ctime])
            #figure out asynchronous messages eventually

            cursor.execute(f"INSERT INTO messages (FIND, AUTHOR, CONTENT, TIMESTAMP) VALUES ({cindex}, '{cauthor}', '{ccontent}', '{ctime}')")
            conn.commit()

            print("message recieved", cauthor)

        case 3: #login
            #print(cleaned_data)
            inputlist = cleaned_data.strip().split("|")
            user_collection = pandas.read_csv('users.csv')
            

            if not(inputlist[0] in user_collection['userid'].tolist()):
                sock.sendto("User not found".encode(), address)
                print("goofy ahh user tried joinin' ")
                return
            
            passhash_lookup = user_collection.loc[user_collection['userid'] == inputlist[0], 'password'].item()
            if inputlist[1] == passhash_lookup:
                sock.sendto("pass".encode(), address)
                
                print(inputlist[0], 'has joined')
                user_authorList[address] = inputlist[0]


while True:
    data, address = sock.recvfrom(4096)
    asyncio.run(handle_message(data, address))
