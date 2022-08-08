import queue
import global_vars, TDMStreamingSerial

packet_queue = queue.Queue()

def capture_packet():
    while True:
        #split the packet by the signature bytes to place each separated packet on the queue
        serial_stream = TDMStreamingSerial.get_serial_data()
    
        list_of_packets = serial_stream.split(b'\xc3\xaa')
        
        #throw out initial partial packet, but to join the packet between two iterations of get_serial_data, join first element of this function call split with last element of previous function call
        if global_vars.buffer_string != "":
            global_vars.buffer_string += list_of_packets[0]
            packet_queue.put(b'\xc3\xaa' + global_vars.buffer_string)
            
        for elem in list_of_packets[1:-1]:
            full_packet = b'\xc3\xaa' + elem #re-add signature bytes to prefix so length of packet stays the same
            packet_queue.put(full_packet)
        
        global_vars.buffer_string = list_of_packets[-1]
        

def get_packet():
    return packet_queue.get()