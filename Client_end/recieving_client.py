#packages
import pickle, queue, socket

PORT = 65432
GUI_queue = queue.Queue()

def main(HOST):
    recieving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    timeout_time = (60.0)*5 #5 minutes
    recieving_socket.settimeout(timeout_time)
    print("Recieving Client trying to connect to Raspberry Pi...")
    try:
        recieving_socket.connect((HOST,PORT))
        print("Recieving Client is connected to Raspberry Pi")
        
        while True:
            try:
                byte_len = recieving_socket.recv(2)
                len_data = int.from_bytes(byte_len, "big")
                data = recieving_socket.recv(len_data)

                try:
                    decoded_data = pickle.loads(data)
                    if decoded_data == "closed_session":
                        recieving_socket.close()
                        print("Closing Recieving Client connection")
                        break
                    
                    elif decoded_data == "No Serial Connection":
                        raise Exception("ERROR: No Serial Connection! Check Connection of Raspberry Pi to Board!")
                        
                    else: 
                        GUI_queue.put(decoded_data)

                except:
                    continue
            except:
                raise Exception("ERROR: Recieving Client timed out! Please relaunch the GUI and the Raspberry Pi to reconnect!")

    except:
        raise Exception("ERROR: Receiving Client couldn't connect to the Raspberry Pi! Please try to relaunch the GUI and the Raspberry Pi to reconnect!")

def get_data():
    return GUI_queue.get()
