import socket
import threading
import uuid
import json
import logging
import time


# server info
PORT_1 = 8000
PORT_2 = 8001
ports = [PORT_1,PORT_2]
HEADER = 64 
# basic length for header, since we do not expect big messages
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'UTF-8'
DISCONNECT = '!DISCONNECT'
print('Socket created')

#logger
logger = logging.getLogger()
formatter = logging.Formatter('%(message)s')
logger.setLevel("INFO")
hdl_file = logging.FileHandler('server_logs.log')
hdl_file.setFormatter(formatter)
logger.addHandler(hdl_file)

sockets = []
for port in ports:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER, port))
    sockets.append(server_socket)

#dict for storing id and code, same as in client.
access_id_code = {}

#8000 handle client. 
def handle_client(conn_1, addr_1):
    print(f'[NEW CONNECTION] {addr_1} connected')
    connected = True
    while connected:
        msg_length = conn_1.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn_1.recv(msg_length).decode(FORMAT)
            if msg[:2] == 'id':  # id starts with letters id (that's how we differ it from other messages)      
                client_id = msg[2:]
                access_code = str(uuid.uuid4()) #generating access code with same id tool. Doesn't matter since it's uniqe.
                access_id_code[client_id] = access_code
                send_code = 'ac' + str(access_code)
                conn_1.send(send_code.encode(FORMAT))
            print(f'{addr_1},{msg}')
            print(access_id_code)
            if msg == '!DISCONNECT':
                connected = False
    conn_1.close()    

#8001 client handeler. 
def handle_client_2(conn_2, addr_2):
    print(f'[NEW CONNECTION] {addr_2} connected')
    connected = True
    while connected:
        rec_msg = conn_2.recv(1024)
        if rec_msg:
            id_code = json.loads(rec_msg)
            print(id_code)
            for k,v in id_code.items():
                # Server gets json - decodes to dict and compares received code with stored pair id:code in dict above. 
                if access_id_code[k] == v:
                    conn_2.send('Access allowed'.encode(FORMAT))
                    logger.log(msg=f'id: {k}, {time.asctime(time.localtime())} access allowed',level=logging.INFO)   
                    print('Access allowed')  
                else:
                    conn_2.send('Access denied. Error, invalid access code'.encode(FORMAT))
                    conn_2.close()
    conn_2.close()    
    

def start_1():

    while True:
        s1 = sockets[0]
        s2 = sockets[1]
        s1.listen(50)
        s2.listen(50)
        for s in sockets:
            conn, addr = s.accept()
            # Didn't know how to quickly get port number from incoming connection via methods, so i got it from conn string. 
            sock_info = str(conn).split(',')
            p1 = sock_info[-3][1:5]
            port_connected = int(p1)
            if port_connected == 8000:
                thread = threading.Thread(target=handle_client, args=(conn, addr)) 
                thread.start()
                print(f'ACTIVE CONNECTIONS S1 {threading.activeCount()- 1}')
            elif port_connected == 8001:
                thread = threading.Thread(target=handle_client_2, args=(conn, addr)) 
                thread.start()
                print(f'ACTIVE CONNECTIONS S1 {threading.activeCount()- 1}')
            else:
                print(str(conn))

print('[STARTING] server is starting...')
start_1()
