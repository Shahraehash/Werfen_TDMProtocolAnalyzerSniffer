import pickle, socket, threading

import TDMCapturePackets, TDMProtocolAnalyzer, TDMStreamingSerial

def main(HOST, PORT):
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sending_socket.bind((HOST,PORT))
    print("Connecting to the Recieving Client")
    sending_socket.listen()
    conn, addr = sending_socket.accept()
    print("Connected to the Recieving Client")
    
    #thread to stream the serial read across the RS485 Bus
    serial_reading_thread = threading.Thread(target = TDMStreamingSerial.stream_serial, )
    serial_reading_thread.start()
    
    #thread to capture the specific packets from the serial read
    capture_packet_thread = threading.Thread(target = TDMCapturePackets.capture_packet, )
    capture_packet_thread.start()

    #thread to Decode the data and prepare it so it can be sent to the GUI
    TDMprotocol_thread = threading.Thread(target = TDMProtocolAnalyzer.TDM_Analyzer, )
    TDMprotocol_thread.start()
    
    
    while True:
        
        raw_TDM_data = TDMProtocolAnalyzer.get_TDM_data()
        if raw_TDM_data != 'closed_session':
            for elem in raw_TDM_data:
                TDM_data_to_send = pickle.dumps([elem])
                
                ##modify this to make it an if statement and observe change
                try:
                    conn.send(len(TDM_data_to_send).to_bytes(2,'big') + TDM_data_to_send) 
                except:
                    continue
                
        else:
            print('in closing state')
            TDMProtocolAnalyzer.empty_queue()
            TDMCapturePackets.empty_queue()
            TDMStreamingSerial.empty_queue()
            closed_session_msg = pickle.dumps(raw_TDM_data)
            conn.send(len(closed_session_msg).to_bytes(2,'big') + closed_session_msg)
            conn.close()
            print("closed the sending server connection")
            break
        

        

        