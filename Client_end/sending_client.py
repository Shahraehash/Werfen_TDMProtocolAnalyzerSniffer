import json, socket

import global_variables

PORT = 65433

def main(HOST, version_of_board, number_of_L4s):
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("sending client trying to connect...")
    sending_socket.connect((HOST,PORT))
    print("sending client is connected to Raspberry Pi")
    
    while True:
        if global_variables.Close_Session:
            sending_socket.close()
            print("closing the sending client connection")
            break

        if global_variables.Hide_Status_Get_Commands:
            Hide_Get_Cmd = 1
        else:
            Hide_Get_Cmd = 0
        data = {"execution tag": global_variables.message, "version of L3 board": version_of_board, "number of L4s": number_of_L4s, "Boolean of Get Command": Hide_Get_Cmd}
        json_data = json.dumps(data)
        encoded_json_data = b'0x00' + json_data.encode('utf-8') + b'0x01'
        sending_socket.send(encoded_json_data)
        #print("sending socket sent:", encoded_json_data, len(encoded_json_data))