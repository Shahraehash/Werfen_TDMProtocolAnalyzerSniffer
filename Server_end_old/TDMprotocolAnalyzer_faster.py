
from TDMDecoder import *
import queue, time 
import global_vars

data_queue = queue.Queue()

def TDM_Analyzer(commandsent):
    ser = serial.Serial(
        port = serial_port_device,
        baudrate = serial_baud_rate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=serial_timeout
    )
 
    time.sleep(0.2) # give the port a moment to open
    
    decoder = TDMDecoder(ser, global_vars.number_of_L4s)

    while True:
        this_host_frame = []
        this_node_frame = []
        if decoder.capture_host_frame() > 0:
            this_host_frame = decoder.host_frame
        else:
            sys.exit("Failed to capture host frame")
            
        for node in range(global_vars.number_of_L4s):
            if decoder.capture_node_frame(node) > 0:
                this_node_frame.append(decoder.node_frame)
            else:
                sys.exit("Failed to capture node frame")

        decoder.is_host_frame_empty(this_host_frame, global_vars.number_of_L4s)
        decoder.is_nodes_frame_empty(this_node_frame, global_vars.number_of_L4s)
        
        
        if not (decoder.node_frame_empty and decoder.host_frame_empty):
            
            final_output_array = []

            if not decoder.host_frame_empty:
                host_frame_array, commandsent = decoder.array_host_frame_decoding(this_host_frame, global_vars.number_of_L4s)
                final_output_array.append(host_frame_array)
            if not decoder.node_frame_empty:
                for node in range(global_vars.number_of_L4s):
                    if decoder.array_node_frame_decoding(this_node_frame[node], node, global_vars.number_of_L4s, commandsent) != None:
                        final_output_array.append(decoder.array_node_frame_decoding(this_node_frame[node], node, global_vars.number_of_L4s, commandsent))
            if len(final_output_array) > 0:
                if global_vars.hide_status_get:
                    if not final_output_array[0][3] == 'COMMAND_status_get':
                        data_queue.put(final_output_array)
                else:
                    data_queue.put(final_output_array)
        if global_vars.close_session:
            data_queue.put("closed_session")
            break


def getData():
    return data_queue.get()

def empty_queue():
    with data_queue.mutex:
        data_queue.queue.clear()
