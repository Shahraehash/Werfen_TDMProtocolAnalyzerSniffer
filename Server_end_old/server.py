# echo-server.py

import socket
import TDMprotocolAnalyzer_faster
import threading
import pickle, time, json

HOST = "192.168.0.1"
#"127.0.0.1"  # Standard loopback interface address (localhost)


PORT = 65432  # Port to listen on (non-privileged ports are > 1023)



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind((HOST, PORT))



def main():
    start_time = time.time()
    
    client_socket.listen()
    conn, addr = client_socket.accept()
    print(f"Connected by {addr}")
    
    initial_data = conn.recv(4096)
    print("took " + str(time.time() - start_time) + " to load")
    all_data = json.loads("[{}]".format(initial_data.decode('utf-8').replace('}{', '},{')))
    initial_decoded_data = all_data[0]
    
    
    TDMprotocolAnalyzer_faster.number_of_L4s = int(initial_decoded_data['number of L4s'])
    
    commandsent = (['NA'], 'NA')
    TDMprotocol_thread = threading.Thread(target = TDMprotocolAnalyzer_faster.TDM_Analyzer, args = (commandsent,))
    TDMprotocol_thread.start()
    
    
    first_time_in_while_loop = True
    while True:
        
        try:
            if first_time_in_while_loop:
                decoded_data = all_data[-1]
            if not first_time_in_while_loop:
                data = conn.recv(4096)
                decoded_data = json.loads(data.decode('utf-8'))
            
            if decoded_data['execution tag'] == 'keep running':
                
                raw_TDM_data = TDMprotocolAnalyzer_faster.getData()
                if decoded_data['Boolean of get Command']:
                    if raw_TDM_data[0][-2] == "COMMAND_status_get":
                        raw_TDM_data = []
                TDM_data_to_send = pickle.dumps(raw_TDM_data)
                conn.send(TDM_data_to_send)
                first_time_in_while_loop = False
        except:
            print("Disconnected ...")
            break
        
        
    time.sleep(2)
    print("Reconnecting")
    first_iteration = False
    main()
                    
                
main()
