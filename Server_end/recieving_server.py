import json, socket

import global_vars

PORT = 65433

def main(HOST):
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.bind((HOST,PORT))
    print("connected to the sending client")
    sending_socket.listen()
    conn, addr = sending_socket.accept()
    while True:
        data = conn.recv(122)
        print(data)
        if data == b'':
            global_vars.close_session = True
            conn.close()
            print("closing the recieving server connection")
            break
        if data[:4] == b'0x00' and data[:-4] == b'0x01':
            data_decoded = data.decode('utf-8')
            json_data_decoded = json.loads(data_decoded)
            global_vars.number_of_L4s = int(json_data_decoded['number of L4s']) 
            if json_data_decoded['Boolean of Get Command'] == '0':
                global_vars.hide_status_get = False
            
    