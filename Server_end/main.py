import threading, time
import recieving_server, sending_server, global_vars

def main():
    HOST = "192.168.0.1"
    
    print("Starting servers")
    recieving_data_server_thread = threading.Thread(target = recieving_server.main, args = (HOST,))
    recieving_data_server_thread.start()
    
    time.sleep(1)
    
    sending_data_server_thread = threading.Thread(target = sending_server.main, args = (HOST,))
    sending_data_server_thread.start()

main()