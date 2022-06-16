# echo-client.py
import socket
import pickle
import queue 
import json

import main

HOST = "192.168.0.1"
#"192.168.100.1"
#"127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

GUI_queue = queue.Queue()


Hide_Status_Get_Commands = False
closing = False

def open_client_socket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("trying to connect...")
        s.connect((HOST, PORT))
        print("Connected to Raspberry Pi")
        message = 'keep running'
        number_of_L4s = main.number_of_L4s
        Hide_Get_Cmd = Hide_Status_Get_Commands
        
        data = {"execution tag": message, "number of L4s": number_of_L4s, "Boolean of get Command": Hide_Get_Cmd}
        json_data = json.dumps(data)
        s.send(json_data.encode('utf-8'))

        while True:
            
            message = 'keep running'
            number_of_L4s = main.number_of_L4s
            Hide_Get_Cmd = Hide_Status_Get_Commands
            
            data = {"execution tag": message, "number of L4s": number_of_L4s, "Boolean of get Command": Hide_Get_Cmd}
            json_data = json.dumps(data)
        
            s.send(json_data.encode('utf-8'))
            data = s.recv(4096)
            client_sends = pickle.loads(data)
            GUI_queue.put(client_sends)
            

            if closing:
                print('closed')
                s.close()
                message = "closed"


def get_data():
    return GUI_queue.get()

def close_connection():
    closing = True