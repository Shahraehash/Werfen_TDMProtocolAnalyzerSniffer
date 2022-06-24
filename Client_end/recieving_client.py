import pickle, queue, socket

import global_variables

PORT = 65432
GUI_queue = queue.Queue()

def main(HOST):
    recieving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recieving_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("recieving client trying to connect...")
    recieving_socket.connect((HOST,PORT))
    print("recieving client is connected to Raspberry Pi")
    host_message = True
    while True:
        if global_variables.Close_Session:
            recieving_socket.close()
            print("closing recieving client connection")
            break

        host_data_input = 0
        node_data_input = 0

        if global_variables.Hide_Status_Get_Commands:
            host_data_input = 861
            node_data_input = 231
        else:
            host_data_input = 865
            node_data_input = 226

        if host_message:
            data = recieving_socket.recv(host_data_input)
            print("recieved host data", len(data))
            host_message = False
        else:
            data = recieving_socket.recv(node_data_input)
            print("recieved node data", len(data))
            host_message = True
        
        try:
            decoded_data = pickle.loads(data)
            #print("decoded_data", decoded_data)
            GUI_queue.put(decoded_data)
        except:
            pass


def get_data():
    return GUI_queue.get()
