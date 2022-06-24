# echo-client.py
from glob import glob
import socket
import pickle
import queue 
import json
import time
import threading
from turtle import goto

import main
import global_variables

HOST = "192.168.0.1"
#"192.168.100.1"
#"127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

GUI_queue = queue.Queue()



def recieve_data(server):
    host_message = True
    while True:
        host_data_input = 0
        node_data_input = 0
        if global_variables.Hide_Status_Get_Commands:
            host_data_input = 861
            node_data_input = 231
        else:
            host_data_input = 865
            node_data_input = 226

        if host_message:
            data = server.recv(host_data_input)
            print("recieved host data", len(data))
            host_message = False
        else:
            data = server.recv(node_data_input)
            print("recieved node data", len(data))
            host_message = True
        server_sends = pickle.loads(data)
        GUI_queue.put(server_sends)


def open_client_socket(number_of_L4s, version_of_board):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    '''
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("trying to connect...")
    s.connect((HOST, PORT))
    print("Connected to Raspberry Pi")
    send_number_of_L4s = number_of_L4s
    if global_variables.Hide_Status_Get_Commands:
        Hide_Get_Cmd = 1
    else:
        Hide_Get_Cmd = 0
    send_version_of_board = version_of_board
    
    data = {"execution tag": global_variables.message, "version of L3 board": send_version_of_board, "number of L4s": send_number_of_L4s, "Boolean of get Command": Hide_Get_Cmd}
    json_data = json.dumps(data)
    encoded_json_data = json_data.encode('utf-8')
    print("encoded json data", data, len(encoded_json_data))
    s.send(encoded_json_data)

    Recieve_Data_Thread = threading.Thread(target = recieve_data, args = (s,))
    Recieve_Data_Thread.start()

    iteration = 0

    while True:
        
        #print(main.close_msg)

        
        number_of_L4s = global_variables.number_of_L4s
        if global_variables.Hide_Status_Get_Commands:
            Hide_Get_Cmd = 1
        else:
            Hide_Get_Cmd = 0
        
        data = {"execution tag": global_variables.message, "version of L3 board": send_version_of_board, "number of L4s": str(number_of_L4s), "Boolean of get Command": Hide_Get_Cmd}
        json_data = json.dumps(data)
        encoded_json_data = json_data.encode('utf-8')
        print("encoded json data", data, len(encoded_json_data))
        s.send(encoded_json_data)
    
        print(iteration)
        iteration += 1
        #time.sleep(0.05)


        if global_variables.closing:
            print("closing socket")
            s.close()
            break

        '''
        host_data_input = 0
        node_data_input = 0
        if global_variables.Hide_Status_Get_Commands:
            host_data_input = 861
            node_data_input = 222
        else:
            host_data_input = 865
            node_data_input = 226

        if host_message:
            data = s.recv(host_data_input)
            print("recieved host data", len(data))
            host_message = False
        else:
            data = s.recv(node_data_input)
            print("recieved node data", len(data))
            host_message = True
        server_sends = pickle.loads(data)
        GUI_queue.put(server_sends)
        '''

def get_data():
    return GUI_queue.get()

