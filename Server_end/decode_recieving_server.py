import queue, time
import global_vars

socket_queue = queue.Queue() 

def decode_recieving_data():
    
    while True:
        data = socket_queue.get()
        
        if global_vars.close_session:
            break
        
        global_vars.number_of_L4s = int(data['number of L4s'])
        if int(data['Boolean of Get Command']) == 0:
            global_vars.hide_status_get = False
        elif int(data['Boolean of Get Command']) == 1:
            global_vars.hide_status_get = True
            
