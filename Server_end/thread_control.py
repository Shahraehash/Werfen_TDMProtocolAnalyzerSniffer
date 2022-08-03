import threading, time
import global_vars, recieving_server, sending_server 

def main():
    global_vars.close_session = False
    
    HOST = "192.168.0.1"
    
    Recieving_Server_Port = 65433
    print("Starting servers")
    recieving_data_server_thread = threading.Thread(target = recieving_server.main, args = (HOST, Recieving_Server_Port))
    recieving_data_server_thread.start()
    
    time.sleep(1)
    Sending_Server_Port = 65432
    sending_data_server_thread = threading.Thread(target = sending_server.main, args = (HOST, Sending_Server_Port))
    sending_data_server_thread.start()
