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
    def __init__(self, ser):
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
        #if self.sync_state != "OUT_OF_SYNC":
        #    if debug: print("Tried to sync while we're already in sync")
        #    return(-1)
            
        if debug: print("Looking for start of Host Frame...")
        start_time = time.time()
        self.sync_state = "OUT_OF_SYNC"
        while idle_timeout == -1 or start_time + idle_timeout > time.time():
            ch = self.serial.read()
            if ch == b'': continue
            if ch[0] == self.signature_byte_0: 
                ch = self.serial.read()
                if ch == b'': continue
                if ch[0] == self.signature_byte_1: 
                    self.sync_state = "IN_SYNC"
                    break
        
        if self.sync_state != "IN_SYNC":
            if debug: print(str(idle_timeout) + " second timeout exceeded while searching for host frame")
            return(-1)
        
        if debug: print("\nCapturing Host Frame: " + f"{self.signature_byte_0:02X} {self.signature_byte_1:02X} ", end='')
        
        self.host_frame = [self.signature_byte_0, self.signature_byte_1]
        for i in range(self.host_frame_length - self.start_signature_length):
            ch = self.serial.read()
            if ch == b'': continue
            
            if debug: print(f"{ch[0]:02X} ", end='')
            self.host_frame.append(ch[0])
        #if debug: print(time.time())
        return(1)
        
        
    # Collect the requisite number of bytes comprising the entire node frame
    # return a list of integers representing the host frame
    def capture_node_frame(self, node):
        if self.sync_state == "OUT_OF_SYNC":
            if debug: print("Tried to capture node frame while out of sync")
            return(-1)
            
        
        self.node_frame = []
        search_start_time = time.time()
        if debug: print("Capturing Node Frame [" + str(node) + "] at " + f"{search_start_time:.5f}" + ": ", end='')
        for i in range(self.node_frame_length):
            ch = self.serial.read()
            
            if i == 0 and time.time() > search_start_time + node_timeout:
                if debug: print("No node responded as of " + f"{time.time():.5f}")
                self.node_frame = [0] * self.node_frame_length
                return(1) 
                
            if ch == b'':
                if time.time() > search_start_time + node_timeout:
                    if debug: print("No node responded as of " + f"{time.time():.5f}")
                    self.node_frame = [0] * self.node_frame_length
                    return(1) 
                continue
            '''
            if (i != 0 and time.time() < search_start_time + node_timeout) or (ch != b''):
            #if debug: print(f"\n{time.time():0.5f}:{ch[0]:02X} ", end='')
                self.node_frame.append(ch[0])
            '''
            self.node_frame.append(ch[0])
           
        if debug: print("")
        return(1)
        
    
    # Generate a human readable representation of a Host Frame
    def decode_host_frame(self, frame):
        self.host_frame_empty = True
        host_frame_decoded = "\tHOST:: "
        host_frame_decoded += "MsgID:" 
        host_frame_decoded += f"0x{((frame[self.serial_counter_offset + 1] << 8) + frame[self.serial_counter_offset]):04X}\n"
        
        #if debug: print(frame, " len: ", len(frame))
        running_host_node_offset = self.host_first_node_offset
        for node in range(number_of_L4s):
            host_frame_decoded += "\t\t[" + str(node) + "]:: " 
            
            host_frame_decoded += "nodeID: " + f"{frame[running_host_node_offset]:02X} "
            if frame[running_host_node_offset] != 0: self.host_frame_empty = False
            running_host_node_offset += self.node_addr_length
            
            try:
                host_frame_decoded += "devID: "  + L4_DEVICE_IDS(frame[running_host_node_offset]).name + " "
            except:
                host_frame_decoded += "devID: "  + f"{frame[running_host_node_offset]:02X} "
            running_host_node_offset += self.device_id_length
            
            try:
                host_frame_decoded += "cmdID: "  + L4_COMMAND_CODES(frame[running_host_node_offset]).name + " "
            except:
                host_frame_decoded += "cmdID: "  + f"{frame[running_host_node_offset]:02X} "
            running_host_node_offset += self.command_id_length
            
            for arg in range(self.number_of_args):
                host_frame_decoded += "arg[" + str(arg) + "]: "
                this_arg = 0
                for arg_byte in range(self.arg_length):
                    this_arg = this_arg + (frame[running_host_node_offset] << (arg_byte * 8))
                    running_host_node_offset += 1
                host_frame_decoded += f"{this_arg:08X} "
            host_frame_decoded += "\n"
        
        # TODO: add CRC check here
        return(host_frame_decoded)
        
    
    # Generate a human readable representation of a Node Frame
    def decode_node_frame(self, frame, pos):
        self.node_frame_empty = True
        node_frame_decoded = "\tNODE[" + str(pos) + "]:: "
        running_node_offset = 0
        
        #if debug: print("\tNODE[" + str(pos) + "]: frame length: " + str(len(frame)))
        if frame[running_node_offset] == 0: 
            node_present = False
        else:
            node_present = True
            self.node_frame_empty = False
        
        if node_present:
            node_frame_decoded += "nodeID: " + f"{frame[running_node_offset]:02X} "
        else:
            node_frame_decoded += "nodeID: " + "-- "
        running_node_offset += self.node_addr_length
            
        
        if node_present:
            node_frame_decoded += "serialID: " + f"{frame[running_node_offset]:04X} "
        else:
            node_frame_decoded += "serialID: " + "-- "
        running_node_offset += self.serial_counter_length
        
            
        if node_present:
            try:
                node_frame_decoded += "status: " + L4_STATUS_CODES(frame[running_node_offset]).name + " "
            except:
                node_frame_decoded += "status: " + f"{frame[running_node_offset]:02X} "
        else:
            node_frame_decoded += "status: " + "-- "
        running_node_offset += self.status_length
        
        
        for data in range(self.number_of_data):
            node_frame_decoded += "arg[" + arg + "]: "
            this_data = 0
            for data_byte in range(self.data_length):
                this_data = (this_data << 8) + frame[running_node_offset]
                running_node_offset += 1
            node_frame_decoded += f"{this_data:08X} "
        
        
        # TODO: add CRC check here
        node_frame_decoded += "\n"
        return(node_frame_decoded)
    
        
    
# define a terminal clearing function
def clear(force=False):

    # for windows
    if force:
        if name == 'nt':
            _ = system('cls')
      
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')

    print("\033[0;0H", end="", flush=True)
    

if __name__ == "__main__":
    raw_file = ''
    txt_file = ''
    print_to_console = False
    continuous = False
    print_to_file = False
    dump_to_file = False
    iteration_count = None
    filter_empty = False
    debug = False
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"hcCvfn:d:r:i:t:",["nodes=","decode=","raw=","iterations=","timeout="])
    except getopt.GetoptError:
        print("Arg error: " + sys.argv[0] + ' -hcCv -n <node_count> -d <decoded_file> -r <raw_file> -i <iteration_count> -t <timeout>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(sys.argv[0] + ' -cCv -n <node_count> -d <decoded_file> -r <raw_file>')
            print('\t -c: print decoded output to Console')
            print('\t -C: print decoded output to Console in continuous stream')
            print('\t -v: print Verbose debug output')
            print('\t -f: filter out frames without content')
            print('\t -n: configure decoder to look for <node_count> L4 nodes. Default is 7.')
            print('\t -d: send decoded output to <decoded_file>')
            print('\t -r: send Raw (ascii hex) output to <raw_file>')
            print('\t -i: capture only <iteration_count> transactions. Default is infinite.')
            print('\t -t: Wait for <timeout> seconds looking for a host frame. Default is infinite.')
            sys.exit()
        elif opt == '-c':
            print_to_console = True
            continuous = False
            clear()
        elif opt == '-C':
            print_to_console = True
            continuous = True
        elif opt == '-v':
            debug = True
        elif opt == '-f':
            filter_empty = True
        elif opt in ("-n", "--nodes"):
            number_of_L4s = int(arg)
        elif opt in ("-r", "--raw"):
            dump_to_file = True
            raw_file = arg
        elif opt in ("-d", "--decode"):
            print_to_file = True
            txt_file = arg
        elif opt in ("-i", "--iterations"):
            iteration_count = int(arg)
        elif opt in ("-t", "--timeout"):
            idle_timeout = int(arg)
    if number_of_L4s is None:
        number_of_L4s = 7
    if not (print_to_console or dump_to_file or print_to_file):
        print("Nothing to do.\n" + sys.argv[0] + ' -hcv -d <decoded_file> -r <raw_file>')
        sys.exit(2)
       
    
    ser = serial.Serial(
        port = serial_port_device,
        baudrate = serial_baud_rate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=serial_timeout
    )
    time.sleep(0.2) # give the port a moment to open
    
    decoder = TDMDecoder(ser)
    
    try:
        if dump_to_file:  
            raw = open(raw_file, "a")
            raw.write("\n#### Logging started " + time.ctime() + "\n")
        if print_to_file: 
            txt = open(txt_file, "a")
            txt.write("\n#### Logging started " + time.ctime() + "\n")
        
        remaining_iterations = iteration_count
        if not continuous: clear(force=True)
        script_start_time = time.time()
        transaction_start_time = time.time() - script_start_time
        transaction_number = 0
        rolling_ave_cnt = 20
        cycle_periods = [0] * rolling_ave_cnt
        while True:
            transaction_number += 1
            if not continuous: clear()

            if remaining_iterations is not None:
                if remaining_iterations == 0:
                    sys.exit("Captured " + str(iteration_count) + " transactions.")
                else:
                    print("Capturing transaction " + str(iteration_count - remaining_iterations + 1)) 
                    remaining_iterations -= 1
            
            this_host_frame = []
            this_node_frame = []
        
            # capture start time and a rolling average of cycle period
            now = time.time() - script_start_time
            period = now - transaction_start_time
            transaction_start_time = now
            cycle_periods.append(period)
            cycle_periods = cycle_periods[-rolling_ave_cnt:]
            rolling_ave = sum(cycle_periods)/rolling_ave_cnt
            if rolling_ave > 0: ave_freq = 1/rolling_ave
            else: ave_freq = 0
            
            
            
            if decoder.capture_host_frame() > 0: this_host_frame = decoder.host_frame
            else: sys.exit("Failed to capture host frame")
            for node in range(number_of_L4s):
                if decoder.capture_node_frame(node) > 0:
                    this_node_frame.append(decoder.node_frame)
                else: sys.exit("Failed to capture node frame")
            # record the raw transaction to a file
            if dump_to_file:
                raw.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(transaction_start_time)) + 
                    "." + str(transaction_start_time).split(".")[1] + "\n\tHOST: ")
                for byte in (this_host_frame):
                    raw.write(f"{byte:02X}")
                raw.write("\n")
                for node in range(number_of_L4s):
                    raw.write("\t\tNODE" + str(node) + ": ")
                    for byte in this_node_frame[node]:
                        raw.write(f"{byte:02X}")
                    raw.write("\n")
            
            # generate human readable decode text if needed
            if print_to_console or print_to_file:
                this_decoded_host_frame = decoder.decode_host_frame(this_host_frame)
                this_decoded_node_frame = []
                node_frames_empty = True
                for node in range(number_of_L4s):
                    this_decoded_node_frame.append(decoder.decode_node_frame(this_node_frame[node], node))
                    if not decoder.node_frame_empty: node_frames_empty = False
                                
            if not continuous:
                # pretty print the transaction to console if needed
                if print_to_console:
                    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(transaction_start_time)) + 
                        "." + f"{transaction_start_time:0.5f}".split(".")[1] + 
                        " ####################### " + f"{rolling_ave*1000:0.2f}" + " mS ####################### " + f"{ave_freq:0.1f}" + " Hz ####################### Count: " + str(transaction_number) + "         ")
                    # skip printing if filter_empty and transaction has no nodeIDs in Host Frame nor Node Frames
                    if not (node_frames_empty and decoder.host_frame_empty):
                        print(this_decoded_host_frame.strip('\n'))
                        for node in range(number_of_L4s):
                            print(this_decoded_node_frame[node].strip('\n'))
            
            if continuous:
                # pretty print the transaction to console if needed
                if print_to_console:
                    # skip printing if filter_empty and transaction has no nodeIDs in Host Frame nor Node Frames
                    if not (node_frames_empty and decoder.host_frame_empty):
                        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(transaction_start_time)) + 
                            "." + f"{transaction_start_time:0.5f}".split(".")[1] + 
                            " ####################### " + f"{rolling_ave*1000:0.2f}" + " mS ####################### " + f"{ave_freq:0.1f}" + " Hz ####################### Count: " + str(transaction_number) + "         ")
                        print(this_decoded_host_frame.strip('\n'))
                        for node in range(number_of_L4s):
                            print(this_decoded_node_frame[node].strip('\n'))


            # pretty print the transaction to file if needed
            if print_to_file:
                txt.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(transaction_start_time)) + 
                    "." + f"{transaction_start_time:0.5f}".split(".")[1] + 
                    " ############################################################################################# Count: " + str(transaction_number) + "           \n")
                txt.write(this_decoded_host_frame)
                for node in range(number_of_L4s):
                    txt.write(this_decoded_node_frame[node])
        
        
        if dump_to_file:  raw.close()
        if print_to_file: txt.close()
            
    
    except KeyboardInterrupt:
        print("Done.")
        pass
