# echo-server.py

import socket
import TDMprotocolAnalyzer_faster
import threading
import pickle

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)




def main():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        commandsent = (['NA'], 'NA')
        TDMprotocol_thread = threading.Thread(target = TDMprotocolAnalyzer_faster.TDM_Analyzer, args = (commandsent,))
        TDMprotocol_thread.start()
        with conn:
            print(f"Connected by {addr}")
            while True:    
                data = conn.recv(1024)
                if data.decode() == 'keep running':
                    TDM_data = pickle.dumps(TDMprotocolAnalyzer_faster.getData())
                    conn.send(TDM_data)
