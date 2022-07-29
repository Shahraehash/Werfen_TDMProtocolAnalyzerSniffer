import queue

GUI_queue = queue.Queue()


def decode_packets():
    while True:

        
        byte_len = recieving_socket.recv(2)
        len_data = int.from_bytes(byte_len, "big")
        data = recieving_socket.recv(len_data)

        try:
            decoded_data = pickle.loads(data)
            if decoded_data != "closed_session":
                GUI_queue.put(decoded_data)
            else: 
                recieving_socket.close()
                print("closing recieving client connection")
                break

        except:
            print("couldn't pickle load data", data)
            continue