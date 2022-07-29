import pickle, socket, threading

import global_vars, TDMprotocolAnalyzer_faster

PORT = 65432

def main(HOST):
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sending_socket.bind((HOST,PORT))
    print("connected to the recieving client")
    sending_socket.listen()
    conn, addr = sending_socket.accept()
    
    commandsent = (['NA'], 'NA')
    TDMprotocol_thread = threading.Thread(target = TDMprotocolAnalyzer_faster.TDM_Analyzer, args = (commandsent,))
    TDMprotocol_thread.start()
    
    while True:
        raw_TDM_data = TDMprotocolAnalyzer_faster.getData()
        if raw_TDM_data != 'closed_session':
            for elem in raw_TDM_data:
                TDM_data_to_send = pickle.dumps([elem])
                print("sent", elem)
                try:            
                    conn.send(len(TDM_data_to_send).to_bytes(2,'big') + TDM_data_to_send) 
                    time.sleep(0.1)
                except:
                    break
        else:
            TDMprotocolAnalyzer_faster.empty_queue()
            closed_session_msg = pickle.dumps(raw_TDM_data)
            conn.send(len(closed_session_msg).to_bytes(2,'big') + closed_session_msg)
            conn.close()
            print("closed the sending server connection")
            break
        
        
        

        