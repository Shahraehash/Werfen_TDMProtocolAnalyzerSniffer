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
        
        if this_host_frame == None and this_node_frames == None:
            continue
        
        counter = decoder.decoding_frame(this_host_frame, this_node_frames, global_vars.number_of_L4s)
       
        for num in range(counter):
            frame = [TDMDecoder.frame_queue.get()]
            
            print("hide status boolean", global_vars.hide_status_get)
            if global_vars.hide_status_get: #when we want to hide the status get commands, filter them out and dont put them on the queue
                if not frame[0][3] == 'COMMAND_status_get':
                    TDM_data_queue.put(frame)
            else:
                TDM_data_queue.put(frame)
        
        '''
        
        print(list(TDMDecoder.frame_queue.queue), "\n")
        frame = TDMDecoder.frame_queue.get()
        print(frame)
        
        if global_vars.hide_status_get: #when we want to hide the status get commands, filter them out and dont put them on the queue
            if not frame[0][3] == 'COMMAND_status_get':
                TDM_data_queue.put(frame)
        else:
            TDM_data_queue.put(frame)
        
        if global_vars.close_session:
            TDM_data_queue.put("closed_session")
            break
        
        #print(this_host_frame, "\n")
        #print(this_node_frame, "\n")
        
        
        #check if the frames are empty
        decoder.is_host_frame_empty(this_host_frame, global_vars.number_of_L4s)
        decoder.is_nodes_frame_empty(this_node_frame, global_vars.number_of_L4s)
        
        #when they arent empty we want to decode them
        if not (decoder.node_frame_empty and decoder.host_frame_empty):
            final_output_array = []
            
            #the decoded host frame
            if not decoder.host_frame_empty:
                host_frame_array, commandsent = decoder.array_host_frame_decoding(this_host_frame, global_vars.number_of_L4s)
                final_output_array.append(host_frame_array)
            
            #the decoded node frame
            if not decoder.node_frame_empty:
                for node in range(global_vars.number_of_L4s):
                    node_frame_array = decoder.array_node_frame_decoding(this_node_frame[node], node, global_vars.number_of_L4s, commandsent)
                    if node_frame_array != None:
                        final_output_array.append(node_frame_array)
        

            #Data to place on the queue for GUI
            if len(final_output_array) > 0:
                if global_vars.hide_status_get: #when we want to hide the status get commands, filter them out and dont put them on the queue
                    if not final_output_array[0][3] == 'COMMAND_status_get':

                        TDM_data_queue.put(final_output_array)
                else:
                    #print('data on queue')
                    TDM_data_queue.put(final_output_array)
            
            if global_vars.close_session:
                TDM_data_queue.put("closed_session")
                break
        '''

def get_TDM_data():
    return TDM_data_queue.get()

def empty_queue():
    with TDM_data_queue.mutex:
        TDM_data_queue.queue.clear()