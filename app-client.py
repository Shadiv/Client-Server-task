import socket
import uuid
import json

# Server info (constants)

PORT_1 = 8000
PORT_2 = 8001
HEADER = 64 
# basic length for header, since we do not expect big messages
SERVER = '192.168.0.234'
FORMAT = 'UTF-8'
DISCONNECT = '!DISCONNECT'
ADDR_1 = (SERVER, PORT_1)
ADDR_2 = (SERVER, PORT_2)

# dictionary for storing pair id : access code
access_id_code = {}
client_id = uuid.uuid4()


#for sending regular messages if needed
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' '* (HEADER - len(send_length)) 
    #setting length to 64
    c.send(send_length)
    c.send(message)

# step 1 - sending client id
def send_id(client_id):
    id_message = 'id'+str(client_id)
    id_message = id_message.encode(FORMAT)
    msg_length = len(id_message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' '* (HEADER - len(send_length))
    c.send(send_length)
    c.send(id_message)
    print('message sent') 
    rec_msg = c.recv(1024).decode(FORMAT)
    # after sending id to port 8000 client receives an access code. String starts with ac (acces code) and then contains actual code, that's why we slice it and add to dict.
    if rec_msg[:2] == 'ac':
        access_code = rec_msg[2:]
        access_id_code[str(client_id)] = access_code
        print(access_id_code)

#last step - sending pair id + code to 8001. Json format - server will receive dict.
def send_access(access_id_code):
    send_access = json.dumps(access_id_code).encode(FORMAT)
    c2.send(send_access)
    rec_msg_2 = c2.recv(1024).decode(FORMAT)
    print(rec_msg_2)
    


c = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #1 socket
c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #2 socket

c.connect(ADDR_1)
print('connected')
send_id(client_id)
c2.connect(ADDR_2)
send_access(access_id_code)