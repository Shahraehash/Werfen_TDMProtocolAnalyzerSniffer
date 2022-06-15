# echo-client.py
import socket
import pickle
import queue 
import json

import GUI

HOST = "192.168.0.1"
#"192.168.100.1"
#"127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

GUI_queue = queue.Queue()

NUMBER_OF_L4s = 7
Recieve_Status_Get_Commands = True

closing = False

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        print("trying to connect...")
        s.connect((HOST, PORT))
        print("Connected to Raspberry Pi")
        while True:
            
            message = 'keep running'
            '''
            number_of_L4s = NUMBER_OF_L4s
            #print(number_of_L4s)
            recieve_get_status_command = Recieve_Status_Get_Commands
            
            x = message + ";" + str(number_of_L4s) + ";" + str(recieve_get_status_command)

            s.send(x.encode())
            '''

            s.send(message.encode())
            data = s.recv(4096)
            #print(data)
            client_sends = pickle.loads(data)
            GUI_queue.put(client_sends)
            

            if closing:
                s.close()
                message = "closed"


def get_data():
    return GUI_queue.get()



def close_connection():
    closing = True