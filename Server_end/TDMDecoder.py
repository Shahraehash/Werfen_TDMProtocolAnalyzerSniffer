#!/bin/python
import TDMCapturePackets
from TDMConstants import L4_DEVICE_IDS, L4_COMMAND_CODES, L4_STATUS_CODES, IS_IN

import queue

frame_queue = queue.Queue()

class TDMDecoder:
    def __init__(self, number_of_L4s):
        self.number_of_L4s = number_of_L4s

        self.host_frame = []
        self.node_frames = []
        
        self.signature_byte_0 = 0xc3
        self.signature_byte_1 = 0xaa
        
        self.host_frame_length = 111
        self.node_frame_length = 18
        
        self.number_of_args = 3
        self.number_of_data = 3        
      
    def capture_frames(self):
        #clear the frames
        self.host_frame = []
        self.node_frames = []
        
        #call function to get the packet
        packet = TDMCapturePackets.get_packet()
        
        #isolate the host frame
        for host_idx in range(self.host_frame_length):
            if host_idx < len(packet):
                self.host_frame.append(packet[host_idx])
            else: 
                self.host_frame.append(0)
        
        #isolate the node frames by node
        for node in range(self.number_of_L4s):
            node_frame = []
            for node_idx in range(self.host_frame_length+(self.node_frame_length*node), self.host_frame_length+(self.node_frame_length*(node+1))):
                if node_idx < len(packet):
                    node_frame.append(packet[node_idx])
                else:
                    node_frame.append(0)
                
            self.node_frames.append(node_frame)

        return self.host_frame, self.node_frames
    
    def decoding_frame(self, host_frame, node_frames):
        #check host_frame is valid and check that node frame is valid
        if hex(host_frame[0]) != hex(self.signature_byte_0) and hex(host_frame[1]) != hex(self.signature_byte_1):
            return 
        if len(host_frame) != self.host_frame_length:
            return
        counter = 0
        for node in range(self.number_of_L4s):
            host_output_list = ["Host Frame"]
            decoded_host_frame, deviceID, commandsent = self.decode_host_frame_for_node(host_frame, host_frame[(15*node)+4:(15*(node+1))+4], host_output_list)
            decoded_corresponding_node_frame = self.decode_node_frame(node, node_frames[node], deviceID, commandsent)
           
            if decoded_corresponding_node_frame != None:
                
                frame_queue.put(list(decoded_host_frame))
                frame_queue.put(list(decoded_corresponding_node_frame))
                counter += 2
            
        return counter
        

            
    
    def decode_host_frame_for_node(self, host_frame, host_frame_for_node, host_output_list):
        #Host Frame
        decoded_host_frame = host_output_list
        
        #Node ID
        decoded_host_frame.append("".join(["Node ", str(host_frame_for_node[0])]))
        
        #Device ID
        devID_decoded = "--"
        if IS_IN.dev_is_in(host_frame_for_node[1]):
            devID_decoded = str(L4_DEVICE_IDS(host_frame_for_node[1]).name)
        decoded_host_frame.append(devID_decoded)
        
        #Command ID
        cmd_decoded = "--"
        if IS_IN.cmd_is_in(host_frame_for_node[2]):
            cmd_decoded = str(L4_COMMAND_CODES(host_frame_for_node[2]).name)
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

        decoded_node_frame.append("".join(["Node ", str(node)]))
        
        #Host Frame
        decoded_node_frame.append("Host Frame")
        
        #Device ID
        decoded_node_frame.append(device)
        
        #Command ID
        decoded_node_frame.append(cmd_sent)
        
        #Status
        status_string = "--"
        if IS_IN.stat_is_in(node_frame[3]):
            status_string = str(L4_STATUS_CODES(node_frame[3]).name)
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
        