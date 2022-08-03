import queue, time
import global_vars, TDMDecoder

TDM_data_queue = queue.Queue()


def TDM_Analyzer(commandsent):
    
    decoder = TDMDecoder.TDMDecoder(global_vars.number_of_L4s)
    
    while True:
        if global_vars.close_session:
            TDM_data_queue.put("closed_session")
            break
        
        #capture the host frames and the node frames
        this_host_frame, this_node_frames = decoder.capture_frames()
        
    
        counter = decoder.decoding_frame(this_host_frame, this_node_frames, global_vars.number_of_L4s)
       
        for num in range(counter):
            frame = [TDMDecoder.frame_queue.get()]
            
            if global_vars.hide_status_get: #when we want to hide the status get commands, filter them out and dont put them on the queue
                if not frame[0][3] == 'COMMAND_status_get':
                    TDM_data_queue.put(frame)
            else:
                TDM_data_queue.put(frame)
        

def get_TDM_data():
    return TDM_data_queue.get()

def empty_queue():
    with TDM_data_queue.mutex:
        TDM_data_queue.queue.clear()