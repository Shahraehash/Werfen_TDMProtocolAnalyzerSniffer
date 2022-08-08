HOST = "192.168.0.1"
Hide_Status_Get_Commands = True
Close_Session = False
message = "keep running"
sent_messages = 0

number_of_unpickleable_data = 0

def conv_byte(elem):
    return (str(elem).split('x')[1][:2] + " ")
