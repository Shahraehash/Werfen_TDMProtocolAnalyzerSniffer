#!/bin/python

import serial, sys, getopt, time
from os import system, name
from TDMconstants import L4_DEVICE_IDS
from TDMconstants import L4_COMMAND_CODES
from TDMconstants import L4_STATUS_CODES

serial_port_device='/dev/ttyS0'
serial_baud_rate=921600
serial_timeout=0.000015 # slightly longer than the length of a 921600 byte
idle_timeout=-1 # timeout in seconds before script gives up waiting for a host frame. -1 is infininte
node_timeout=0.0001 #3 # typically about 260uS from end of host frame to start of first node frame per L4 Bus Protocol Spec
number_of_L4s=None

class TDMDecoder:
    def __init__(self, ser, number_of_L4s):
        self.serial = ser
        self.sync_state = "OUT_OF_SYNC"
        self.host_frame = []
        self.node_frame = []
        
        self.signature_byte_0 = 0xC3
        self.signature_byte_1 = 0xAA
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
            
                
        
        
    # Watch the serial port for the host frame signature
    # once found, collect the requisite number of bytes comprising the entire host frame
    # return a list of integers representing the host frame
    def capture_host_frame(self):
        start_time = time.time()
        self.sync_state = "OUT_OF_SYNC"
        while idle_timeout == -1 or start_time + idle_timeout > time.time():
            try:
                ch = self.serial.read()
                if ch == b'': continue
                if ch[0] == self.signature_byte_0: 
                    ch = self.serial.read()
                    if ch == b'': continue
                    if ch[0] == self.signature_byte_1: 
                        self.sync_state = "IN_SYNC"
                        break
            except:
                break
        
        if self.sync_state != "IN_SYNC":
            return(-1)
        
        self.host_frame = [self.signature_byte_0, self.signature_byte_1]
        host_frame = []
        for i in range(self.host_frame_length - self.start_signature_length):
            ch = self.serial.read()
            if ch == b'': continue
   
            self.host_frame.append(ch[0])

        return(1)
        
        
    # Collect the requisite number of bytes comprising the entire node frame
    # return a list of integers representing the host frame
    def capture_node_frame(self, node):
        if self.sync_state == "OUT_OF_SYNC":
            return(-1)
            
        
        self.node_frame = []
        search_start_time = time.time()
        for i in range(self.node_frame_length):
            try: 
                ch = self.serial.read()
                
                if i == 0 and time.time() > search_start_time + node_timeout:
                    self.node_frame = [0] * self.node_frame_length
                    return(1) 
                    
                if ch == b'':
                    if time.time() > search_start_time + node_timeout:
                        self.node_frame = [0] * self.node_frame_length
                        return(1) 
                    continue
            except:
                continue
            
            self.node_frame.append(ch[0])
        return(1)
        
    def is_host_frame_empty(self, frame, number_of_L4s):
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
        return output_list, ([str(node_commandsentto)], devID_decoded, cmd_decoded)

   
    def is_nodes_frame_empty(self, frame, number_of_L4s):
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