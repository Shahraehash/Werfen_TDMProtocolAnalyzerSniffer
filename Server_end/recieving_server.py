import json, socket, threading

import decode_recieving_server, global_vars, TDMProtocolAnalyzer

def main(HOST, PORT):
    recieving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recieving_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recieving_socket.bind((HOST,PORT))
    print("Connecting to the Sending Client")
    recieving_socket.listen()

    conn, addr = recieving_socket.accept()
    print("Connected to the Sending Client")

    decoding_recieve_thread = threading.Thread(target = decode_recieving_server.decode_recieving_data, )
    decoding_recieve_thread.start()

    recieving_byte_data = 4400
    while True:
        data_list = conn.recv(recieving_byte_data).split(b'0xst')

        for data in data_list[-5:]:
            if len(data) == 88:
                decoded_data = data.decode('utf-8')
                decode_recieving_server.socket_queue.put(json.loads(decoded_data))
            elif data == b'closed_socket':
                global_vars.close_session = True
                global_vars.hide_status_get = True
                TDMProtocolAnalyzer.TDM_data_queue.put('closed_session')
                conn.close()
                print("closed the recieving server connection")
                break
        
        if global_vars.close_session:
            break

       
