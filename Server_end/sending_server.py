import pickle, socket, threading

import global_vars, TDMprotocolAnalyzer_faster


PORT = 65432

def main(HOST):
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.bind((HOST,PORT))
    print("connected to the recieving client")
    sending_socket.listen()
    conn, addr = sending_socket.accept()
    
    commandsent = (['NA'], 'NA')
    TDMprotocol_thread = threading.Thread(target = TDMprotocolAnalyzer_faster.TDM_Analyzer, args = (commandsent,))
    TDMprotocol_thread.start()
    
    while True:
        if global_vars.close_session:
            TDMprotocolAnalyzer_faster.empty_queue()
            conn.close()
            print("closed the sending server connection")
            break
        else:
            raw_TDM_data = TDMprotocolAnalyzer_faster.getData()
            for elem in raw_TDM_data:
                TDM_data_to_send = pickle.dumps([elem])
                try:            
                    conn.send(TDM_data_to_send)
                    print("data sent", len(TDM_data_to_send))
                    time.sleep(0.1)
                except:
                    break
        
    
