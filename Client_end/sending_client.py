#packages
import json, socket

#python scripts
import global_variables

PORT = 65433

def main(HOST, number_of_L4s):
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Sending Client trying to connect to Raspberry Pi...")
    try: 
        sending_socket.connect((HOST,PORT))
        print("Sending Client is connected to Raspberry Pi")
        while True:
            if global_variables.Hide_Status_Get_Commands:
                Hide_Get_Cmd = 1
            else:
                Hide_Get_Cmd = 0
            
            data = {"execution tag": global_variables.message, "number of L4s": number_of_L4s, "Boolean of Get Command": Hide_Get_Cmd}
            json_data = json.dumps(data)
            encoded_json_data = json_data.encode('utf-8') + b'0xst'


            if global_variables.Close_Session:
                closing_msg = "closed_socket"
               

                sending_socket.send(closing_msg.encode('utf-8') + b'0xst')
                sending_socket.close()
                global_variables.sent_messages = 0
                print("Closing Sending Client connection")
                break

            
            sending_socket.send(encoded_json_data)
            global_variables.sent_messages += 1

    except:
        print("ERROR: Couldn't connect to Raspberry Pi! Please relaunch GUI and Raspbery Pi!")
    
    
    