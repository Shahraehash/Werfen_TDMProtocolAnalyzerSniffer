import pickle, queue, socket, time 

import global_variables

PORT = 65432
GUI_queue = queue.Queue()

def main(HOST):
    recieving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    timeout_time = (60.0)*5
    recieving_socket.settimeout(timeout_time)
    print("recieving client trying to connect...")
    recieving_socket.connect((HOST,PORT))
    print("recieving client is connected to Raspberry Pi")
    
    while True:

        byte_len = recieving_socket.recv(2)
        len_data = int.from_bytes(byte_len, "big")
        data = recieving_socket.recv(len_data)

        try:
            decoded_data = pickle.loads(data)
            if decoded_data != "closed_session":
                GUI_queue.put(decoded_data)
            else: 
                recieving_socket.close()
                print("closing recieving client connection")
                break

        except:
            global_variables.number_of_unpickleable_data += 1
            if global_variables.number_of_unpickleable_data == 1000:
                break
            continue


def get_data():
    return GUI_queue.get()
