#!/bin/python
import global_vars, TDMCapturePackets
from TDMConstants import L4_DEVICE_IDS
from TDMConstants import L4_COMMAND_CODES
from TDMConstants import L4_STATUS_CODES

import queue

frame_queue = queue.Queue()

class TDMDecoder:
    def __init__(self, number_of_L4s):
    
        self.host_frame = []
        self.node_frames = []
        
        self.signature_byte_0 = 0xc3
        self.signature_byte_1 = 0xaa
        
        self.host_frame_length = 111
        self.node_frame_length = 18
        
        self.number_of_args = 3
        self.number_of_data = 3
        
        #self.frame_queue = queue.Queue()
        
        '''
        self.start_signature_length = 2
        self.serial_counter_length = 2
        self.node_addr_length = 1
        self.device_id_length = 1
        self.command_id_length = 1
        self.status_length = 1
        self.data_length = 4
        self.number_of_data = 3
        self.arg_length = 4
        self.number_of_args = 3
        self.crc_length = 2
        
        self.serial_counter_offset = self.start_signature_length
        self.host_first_node_offset = self.serial_counter_offset + self.serial_counter_length
        self.host_node_addr_offset = 0
        self.host_node_device_offset = self.host_node_addr_offset + self.node_addr_length
        self.host_node_command_offset = self.host_node_device_offset + self.device_id_length
        self.host_node_first_arg_offset = self.host_node_command_offset + self.command_id_length
        
      
        self.host_frame_length =             \
            self.start_signature_length +    \
            self.serial_counter_length +     \
            (                                \
                (                            \
                    self.node_addr_length +  \
                    self.device_id_length +  \
                    self.command_id_length + \
                    (                        \
                        self.arg_length *    \
                        self.number_of_args  \
                    )                        \
                ) *                          \
                number_of_L4s                \
            ) +                              \
            self.crc_length
    
        self.node_frame_length =             \
            self.node_addr_length +          \
            self.device_id_length +          \
            self.command_id_length +         \
            self.status_length +             \
            (                                \
                self.data_length *           \
                self.number_of_data          \
            ) +                              \
            self.crc_length
        '''
    def capture_frames(self):
        #clear the frames
        self.host_frame = []
        self.node_frames = []
        
        #call function to get the packet
        packet = TDMCapturePackets.get_packet()
        
        '''
        if packet == None:
            return None, None
        '''
        
        #isolate the host frame
        for host_idx in range(self.host_frame_length):
            self.host_frame.append(packet[host_idx]) 
        
        #print(self.host_frame)
        
        #isolate the node frames by node
        for node in range(global_vars.number_of_L4s):
            node_frame = []
            for node_idx in range(self.host_frame_length+(self.node_frame_length*node), self.host_frame_length+(self.node_frame_length*(node+1))):
                try:
                    node_frame.append(packet[node_idx])
                except: #if there is no response from a node since it doesnt exist on the bus
                    node_frame.append(0)
            self.node_frames.append(node_frame)
        #print(packet, self.host_frame, self.node_frames, "\n")
        return self.host_frame, self.node_frames
    
    def decoding_frame(self, host_frame, node_frames, number_of_L4s):
        #check host_frame is valid and check that node frame is valid
        #print("frames:", host_frame, node_frames, )
        if hex(host_frame[0]) != hex(self.signature_byte_0) and hex(host_frame[1]) != hex(self.signature_byte_1):
            #print('no sig byte')
            return 
        if len(host_frame) != self.host_frame_length:
            #print('improper length')
            return
        counter = 0
        for node in range(int(number_of_L4s)):
            host_output_list = ["Host Frame"]
            decoded_host_frame, deviceID, commandsent = self.decode_host_frame_for_node(node, host_frame, host_frame[(15*node)+4:(15*(node+1))+4], host_output_list)
            decoded_corresponding_node_frame = self.decode_node_frame(node+1, node_frames[node], deviceID, commandsent)
            #print(decoded_host_frame, decoded_corresponding_node_frame)
            if decoded_corresponding_node_frame != None:
                #print(decoded_host_frame, decoded_corresponding_node_frame, "\n")
                #print(list(frame_queue.queue))
                #print(decoded_host_frame, decoded_corresponding_node_frame, counter)
                frame_queue.put(list(decoded_host_frame))
                frame_queue.put(list(decoded_corresponding_node_frame))
                counter += 2
            
        return counter
        

            
    
    def decode_host_frame_for_node(self, node, host_frame, host_frame_for_node, host_output_list):
        #Host Frame
        decoded_host_frame = host_output_list
        
        #Node ID
        decoded_host_frame.append("".join(["Node ", str(host_frame_for_node[0])]))
        
        #Device ID
        devID_decoded = ""
        try:
            devID_decoded = L4_DEVICE_IDS(host_frame_for_node[1]).name
        except:
            devID_decoded = "--"
        decoded_host_frame.append(devID_decoded)
        
        #Command ID
        cmd_decoded = ""
        try:
            cmd_decoded = str(L4_COMMAND_CODES(host_frame_for_node[2]).name)
        except:
            cmd_decoded = "--"
        decoded_host_frame.append(cmd_decoded)
        
        #Status
        decoded_host_frame.append("--")
        
        #Arguments
        for arg in range(self.number_of_args):
            arguments_decoded = ""
            args = "arg[" + str(arg) + "]: "
            this_arg = 0
            for idx in range(4):
                #args += str(hex(host_frame_for_node[4*arg+idx+3]))
                this_arg = this_arg + ((host_frame_for_node[4*arg+idx+3]) << (idx *8))
            arguments_decoded += "".join([args, f"{this_arg:08X} "])
            decoded_host_frame.append(arguments_decoded)
      
                
        #Byte Code
        byte_code_list = []
        for elem in host_frame:
            byte_code_list += ["0x{:02x}".format(elem)]
        decoded_host_frame.append(byte_code_list)
            
        return decoded_host_frame, devID_decoded, cmd_decoded
    
    def decode_node_frame(self, node, node_frame, device, cmd_sent):
        decoded_node_frame = []
        
        #Node ID
        node = node_frame[0]
        if node == 0:
            return None
        decoded_node_frame.append("".join(["Node ", str(node)]))
        
        #Host Frame
        decoded_node_frame.append("Host Frame")
        
        #Device ID
        decoded_node_frame.append(device)
        
        #Command ID
        decoded_node_frame.append(cmd_sent)
        
        #Status
        status_string = ""
        try:
            status_string = L4_STATUS_CODES(node_frame[3]).name
        except:
            status_string = "--"
        decoded_node_frame.append(status_string)
        
        #Data
        for data in range(self.number_of_data):
            data_decoded = ""
            data_str = "data[" + str(data) + "]: "
            this_data = 0
            for idx in range(4):
                this_data = this_data + (node_frame[4*data+idx+3] << (idx * 8))
                #data_str += str(node_frame[4*data+idx+3])) + " "
            data_decoded = "".join([data_str, f"{this_data:08X} "])
            decoded_node_frame.append(data_decoded)
        

        #Byte Code
        byte_code_list = []
        for elem in node_frame:
            byte_code_list += ["0x{:02x}".format(elem)]
        decoded_node_frame.append(byte_code_list)
        
        return decoded_node_frame
        
        
    '''
    def is_host_frame_empty(self, frame, number_of_L4s):
        #checks if the frame is empty
        self.host_frame_empty = True
        running_host_node_offset = self.host_first_node_offset
        for node in range(number_of_L4s):
            if frame[running_host_node_offset] != 0:
                self.host_frame_empty = False
        return
    
    def array_host_frame_decoding(self, frame, number_of_L4s):
        running_host_node_offset = self.host_first_node_offset
        #Source
        output_list = ["Host Frame"]
        
        #Destination - nodeID information
        node_commandsentto = frame[running_host_node_offset]
        nodeID_decoded = "".join(["node ", f"{node_commandsentto:02X} "])
        output_list.append(nodeID_decoded)
        running_host_node_offset += self.node_addr_length
        
        #DeviceID
        devID_decoded = ""
        try:
            devID_decoded = L4_DEVICE_IDS(frame[running_host_node_offset]).name
        except:
            devID_decoded = "--"
        running_host_node_offset += self.device_id_length
        output_list.append(devID_decoded)
        
        #Commands
        cmd_decoded = ""
        try:
            cmd_decoded = str(L4_COMMAND_CODES(frame[running_host_node_offset]).name)
        except:
            cmd_decoded = "--"
        running_host_node_offset += self.command_id_length
        output_list.append(cmd_decoded)
        
        #Status
        output_list.append("--")
        
        #Additional Arguments
        for arg in range(self.number_of_args):
            arguments_decoded = ""
            args_decoded = "arg[" + str(arg) + "]: "
            this_arg = 0
            for arg_byte in range(self.arg_length):
                this_arg = this_arg + (frame[running_host_node_offset] << (arg_byte * 8))
                running_host_node_offset += 1
            arguments_decoded = "".join([arguments_decoded, args_decoded, f"{this_arg:08X} "])
            output_list.append(arguments_decoded)
        
        
        #Byte-Code
        byte_code_list = []
        for elem in frame:
            byte_code_list += ["0x{:02x}".format(elem)]
        
        output_list.append(byte_code_list)
        
        print(frame, output_list)
        return output_list, ([str(node_commandsentto)], devID_decoded, cmd_decoded)

   
    def is_nodes_frame_empty(self, frame, number_of_L4s):
        #checks if all of the node frames are empty
        self.node_frame_empty = True
        running_node_offset = 0
        nodeID = [i for i in range(number_of_L4s)]
        for node in range(number_of_L4s):
            subframe = frame[node]
            if subframe[running_node_offset] == 0 or subframe[running_node_offset] not in nodeID:
                continue
            else:
                self.node_frame_empty = False
        return
    
    def array_node_frame_decoding(self, frame, pos, number_of_L4s, commandsent):
        valid_nodeID = [str(i) for i in range(number_of_L4s)]
        running_node_offset = 0
        #print(commandsent)
        node_commandsentto, device, command = commandsent
        if str(frame[running_node_offset]) in valid_nodeID and str(frame[running_node_offset]) in node_commandsentto:
            output_node_list = []
            
            #Source
            nodeID_decoded = "".join(["node ", f"{frame[running_node_offset]:02X} "])
            running_node_offset += self.node_addr_length
            running_node_offset += self.serial_counter_length
            output_node_list.append(nodeID_decoded)
            
            #Destination
            output_node_list.append("Host Frame")
            
            #Device
            output_node_list.append(device)
            
            #Command
            output_node_list.append(command)
            
            #Status
            status_string = ""
            try:
                status_string = L4_STATUS_CODES(frame[running_node_offset]).name
            except:
                status_string = "--"
            output_node_list.append(status_string)
            running_node_offset += self.status_length
            
            #Arguments
            for data in range(self.number_of_data):
                arguments_decoded = ""
                node_frame_decoded = "arg[" + str(data) + "]: "
                this_data = 0
                for data_byte in range(self.data_length):
                    this_data = (this_data << 8) + frame[running_node_offset]
                    running_node_offset += 1
                arguments_decoded = "".join([arguments_decoded, node_frame_decoded, f"{this_data:08X} "])
                output_node_list.append(arguments_decoded)
            
            
            #Byte-Code
            byte_code_list = []
            for elem in frame:
                byte_code_list += ["0x{:02x}".format(elem)]
            
            output_node_list.append(byte_code_list)
            return output_node_list
        else:
            return
    '''