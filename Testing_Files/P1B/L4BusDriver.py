#!/usr/bin/python3
import subprocess, sys, time, mmap, resource, os, threading, struct
from TDMconstants import L4_DEVICE_IDS
from TDMconstants import L4_COMMAND_CODES
from TDMconstants import L4_STATUS_CODES

DEFAULT_NODE_COUNT = 7



class L4BusDriver:
    def __init__(self, base_addr=0x40040000, max_l4s=DEFAULT_NODE_COUNT, debug=False):

        self.debug = debug
        self.base_address = base_addr
        self.max_l4_count = max_l4s
        self.fast485_running = False
        self.always_send_get_status = False
        self.cycle_time = 20000 # microseconds
        self.cfifo_thr_full = 0x06
        self.cfifo_thr_empty = 0x03
        self.rfifo_thr_full = 0x04
        self.rfifo_thr_empty = 0x01
        self.host_frame_segment_length = self.max_l4_count * 16  # a complete host frame node segment is 4 32b words per node

        
        
        self.cmd_addr             = 0x0000
        self.irq_mask_p_addr      = 0x0004
        self.irq_mask_n_addr      = 0x0008
        self.irq_clear_addr       = 0x000C
        self.irq_status_addr      = 0x0010
        self.status_addr          = 0x0014
        self.config_addr          = 0x0018
        
        self.rev_id_addr          = 0x001C
        self.brd_id_addr          = 0x0020
        self.fifo_cmd_addr        = 0x0024
        self.fifo_resp_addr       = 0x0028
        self.soft_control_addr    = 0x0030
        self.cfifo_thr_full_addr  = 0x0034
        self.cfifo_thr_empty_addr = 0x0038
        self.rfifo_thr_full_addr  = 0x003C
        self.rfifo_thr_empty_addr = 0x0040
        self.t_cycle_addr         = 0x0044
        self.DISCOVERY_T1_addr    = 0x0048
        self.DISCOVERY_T2_addr    = 0x004C
        self.DISCOVERY_T3_addr    = 0x0050
        self.DISCOVERY_T4_addr    = 0x0054
        self.T_HEARTBEAT_addr     = 0x0058
        self.an_pointer_addr      = 0x005C
        self.cm_pointer_addr      = 0x0060
        
        self.cm_bram_addr         = 0x4000
        self.an_bram_addr         = 0x2000
        
        self.CMD_CLEAR_OP          = 0x01
        self.CMD_START_485_RUNNING = 0x02
        self.CMD_STOP_485_RUNNING  = 0x03
        self.CMD_STOP_RECORDING    = 0x04
        self.CMD_START_RECORDING   = 0x05
        self.CMD_DISCOVERY         = 0x06
        self.CMD_FAULT             = 0x08
        self.logic_analyzer_flag   = 0x55

        self.STATUS_DEF = [ \
            "Command Complete              ", \
            "Illegal Command               ", \
            "Error Detected                ", \
            "Command FIFO Overflow         ", \
            "Command FIFO Underflow        ", \
            "Command FIFO Empty            ", \
            "Command FIFO Full             ", \
            "Command FIFO Threshold Full   ", \
            "Command FIFO Threshold Empty  ", \
            "Recieve FIFO Overflow         ", \
            "Recieve FIFO Underflow        ", \
            "Recieve FIFO Empty            ", \
            "Recieve FIFO Full             ", \
            "Recieve FIFO Threshold Full   ", \
            "Recieve FIFO Threshold Empty  ", \
            "CRC Error                     ", \
            "Short Bit Error               ", \
            "Reserved                      ", \
            "Stop Bit Error                ", \
            "Response out of cycle         ", \
            "Discovery Complete            ", \
            "Alert Pulse Detected          "]
            
        
        self.STATUS_COMMAND_COMPLETE              = 0b00000000000000001
        self.STATUS_ILLEGAL_COMMAND               = 0b00000000000000010
        self.STATUS_ERROR_DETECTED                = 0b00000000000000100
        self.STATUS_COMMAND_FIFO_OVERFLOW         = 0b00000000000001000
        self.STATUS_COMMAND_FIFO_UNDERFLOW        = 0b00000000000010000
        self.STATUS_COMMAND_FIFO_EMPTY            = 0b00000000000100000
        self.STATUS_COMMAND_FIFO_FULL             = 0b00000000001000000
        self.STATUS_COMMAND_FIFO_THRESHOLD_FULL   = 0b00000000010000000
        self.STATUS_COMMAND_FIFO_THRESHOLD_EMPTY  = 0b00000000100000000
        self.STATUS_RECIEVE_FIFO_OVERFLOW         = 0b00000001000000000
        self.STATUS_RECIEVE_FIFO_UNDERFLOW        = 0b00000010000000000
        self.STATUS_RECIEVE_FIFO_EMPTY            = 0b00000100000000000
        self.STATUS_RECIEVE_FIFO_FULL             = 0b00001000000000000
        self.STATUS_RECIEVE_FIFO_THRESHOLD_FULL   = 0b00010000000000000
        self.STATUS_RECIEVE_FIFO_THRESHOLD_EMPTY  = 0b00100000000000000
        self.STATUS_CRC_ERROR                     = 0b01000000000000000
        self.STATUS_SHORT_BIT_ERROR               = 0b10000000000000000  
            
            
            
        self.fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)

        self.mmap_csr  = mmap.mmap(self.fd, resource.getpagesize(), mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=self.base_address)

        self.mmap_cram = []
        for i in range(8):
            self.mmap_cram.append(mmap.mmap(self.fd, resource.getpagesize(), mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=self.base_address + self.cm_bram_addr + (i * 0x1000)))

        self.mmap_aram = []
        for i in range(8):
            self.mmap_aram.append(mmap.mmap(self.fd, resource.getpagesize(), mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=self.base_address + self.an_bram_addr + (i * 0x1000)))


     


        self.response_thread = threading.Thread(target=self.poll_for_responses, args=())
        self.response_thread_enable = False
        self.response_thread_kill = False
        self.response_thread.daemon = True
        self.response_thread.start()
        self.running_serial_id = 1
 
        self.init_fast_485()        
        
    
    def report_status(self):
        status_value = self.read_csr(self.status_addr)
        print("Fast 485 Status Register Contents:")
        for i in range(32):
            if status_value & 1 == 1:
                try:
                    print("bit[" + str(i) + "]: " + self.STATUS_DEF[i])
                except: 
                    print("bit[" + str(i) + "]: Undefined Status")
            status_value = status_value >> 1


    def fpga_write32(self, addr, data):
        return_status = subprocess.call(["devmem", f"0x{addr:X}", "32", f"0x{data:X}"])
        if self.debug: print(f"[devmem wr32 0x{addr:X} <- 0x{data:X}]")
        if return_status != 0: sys.exit(f"failed to write fpga addr 0x{addr:X}") 
        
    def fpga_read32(self, addr, silent=False):
        data = int(subprocess.check_output(["devmem", f"0x{addr:X}", "32"]), 16)
        if self.debug and not silent: print(f"[devmem rd32 0x{addr:X} -> 0x{data:X}]")
        return data


    #memoryview added to maintain automic 32b reads/write to AXI bus
    def read_csr(self, addr, silent=False):
        self.mmap_csr.seek(addr)
        self.mv_csr = memoryview(self.mmap_csr)
        mv_as_int32 = self.mv_csr.cast('I')  # Note "I" works as intended, "L" still results in duplicate writes; "LL" is not an option
        data = mv_as_int32[addr // 4]  # this works; results in 1 write issued on the AXI bus
        #data = int.from_bytes(self.mmap_csr.read(4), 'little')
        if self.debug and not silent: print(f"[mmap rd32 0x{addr:X} -> 0x{data:X}]")        
        return(data)

    #memoryview added to maintain automic 32b reads/write to AXI bus
    def write_csr(self, addr, data):
        if self.debug: print(f"[mmap wr32 0x{addr:X} <- 0x{data:X}]")
        self.mmap_csr.seek(addr)
        self.mv_csr = memoryview(self.mmap_csr)
        mv_as_int32 = self.mv_csr.cast('I')  # Note "I" works as intended, "L" still results in duplicate writes; "LL" is not an option
        mv_as_int32[addr // 4] = data  # this works; results in 1 write issued on the AXI bus
        self.mmap_csr.write(int.to_bytes(data, 4, 'little'))
        
        
        
    ### these versions of read/write_csr didn't maintain automic 32b reads/writes to the FPGA
    def orig_read_csr(self, addr, silent=False):
        self.mmap_csr.seek(addr)
        data = int.from_bytes(self.mmap_csr.read(4), 'little')
        if self.debug and not silent: print(f"[mmap rd32 0x{addr:X} -> 0x{data:X}]")        
        return(data)

    def orig_write_csr(self, addr, data):
        if self.debug: print(f"[mmap wr32 0x{addr:X} <- 0x{data:X}]")
        self.mmap_csr.seek(addr)
        self.mmap_csr.write(int.to_bytes(data, 4, 'little'))
        
        
    def read_cmd_ram(self, addr):
        for map in range(8):
            if addr >= (map * 0x1000) and addr < ((map * 0x1000) + 0x1000):
                self.mmap_cram[map].seek(addr)
                return(int.from_bytes(self.mmap_cram[map].read(4), 'little'))
        sys.exit("Read from command ram out of range.")
    
    def write_cmd_ram(self, addr, data):
        if self.debug: print((["mmap cram write: ", f"0x{addr:X}", "32", f"0x{data:X}"]))
        for map in range(8):
            if addr >= (map * 0x1000) and addr < ((map * 0x1000) + 0x1000):
                self.mmap_cram[map].seek(addr)
                self.mmap_cram[map].write(int.to_bytes(data, 4, 'little'))
                return
        sys.exit("Write to command ram out of range: " + f"0x{addr:08X} 0x{data:08X}")
        
    
    def read_ananlyzer_ram(self, addr):
        for map in range(8):
            if addr >= (map * 0x1000) and addr < ((map * 0x1000) + 0x1000):
                self.mmap_aram[map].seek(addr)
                return(int.from_bytes(self.mmap_aram[map].read(4), 'little'))
        sys.exit("Read from analyzer ram out of range.")
    
    def read_ananlyzer_ram(self, addr, data):
        for map in range(8):
            if addr >= (map * 0x1000) and addr < ((map * 0x1000) + 0x1000):
                self.mmap_aram[map].seek(addr)
                self.mmap_aram[map].write(int.to_bytes(data, 4, 'little'))
                return
        sys.exit("Write to analyzer ram out of range.")
        
    
    def disable_fast_485(self):
        ## This disconnects FPGA IOs from the Fast485 IP (allowing use of an alternate IP like 16550 UART)
        orig = self.fpga_read32(0x40010000)
        self.fpga_write32(0x40010000, orig & 0xFFEFFFFF)

    def enable_fast_485(self):
        ## This connects FPGA IOs to the Fast485 IP 
        orig = self.fpga_read32(0x40010000)
        self.fpga_write32(0x40010000, orig | 0x00100000)
        
        
    def stop(self):
        # stop the Fast485 FPGA IP
        if self.debug: print("Stopping Fast485.")
        self.response_thread_enable = False
        self.write_csr(self.cmd_addr, self.CMD_STOP_485_RUNNING) 
        
    def start(self):
        # start the 485 interface running
        if self.debug: print("Starting Fast485.")  
        self.response_thread_enable = True
        self.write_csr(self.cmd_addr, self.CMD_START_485_RUNNING)

    def clear(self):
        # clear Command register and set the command and analyzer pointers to beginning (lowest address) of the RAM
        if self.debug: print("Clearing Fast485.")
        self.write_csr(self.cmd_addr, self.CMD_CLEAR_OP)
    
       
    def init_fast_485(self):
        
        # stop the Fast485 FPGA IP
        self.stop()
    
        # enable the Fast485 FPGA IP
        if self.debug: print("Selecting Fast485 and not 16550 UART.")
        self.enable_fast_485()
        
        # clear the first transaction location in command ram to define the repeating default get status message
        if self.debug: print("Configuring status request frame in Command RAM")
        self.init_command_ram()
        
        # if debug mode, fill command ram with address locations
        #if self.debug: self.cmd_ram_debug_loader()
        
        # configure software control register with a default logic analyzer flag and max L4 node count
        if self.debug: print("Configuring Fast485 analyzer flag = " + f"0x{self.logic_analyzer_flag:04X}")
        if self.debug: print("Configuring Fast485 max L4 count = " + str(self.max_l4_count))
        self.write_csr(self.soft_control_addr, (self.logic_analyzer_flag << 16) + (self.max_l4_count << 8))
        
        # for debugging only!
        # configure software control register to disable certain error types
        if self.debug: 
            print("Disabling FPGA CRC Check")
            self.write_csr(self.soft_control_addr, self.read_csr(self.soft_control_addr) | 0x2)
            print("Disabling FPGA FIFO overrun/underrun check")
            self.write_csr(self.soft_control_addr, self.read_csr(self.soft_control_addr) | 0x4)
            print("Disabling FPGA response framing error check")
            self.write_csr(self.soft_control_addr, self.read_csr(self.soft_control_addr) | 0x8)



        
        # configure FIFO tresholds
        if self.debug: print("Configuring Fast485 FIFO thresholds (cmd full/empty & rcv full/empty) = " + f"0x{self.cfifo_thr_full:03X}/0x{self.cfifo_thr_empty:03X} & 0x{self.rfifo_thr_full:03X}/0x{self.rfifo_thr_empty:03X}")
        self.write_csr(self.cfifo_thr_full_addr,  self.cfifo_thr_full  )
        self.write_csr(self.cfifo_thr_empty_addr, self.cfifo_thr_empty )
        self.write_csr(self.rfifo_thr_full_addr,  self.rfifo_thr_full  )
        self.write_csr(self.rfifo_thr_empty_addr, self.rfifo_thr_empty )
        self.write_csr(self.irq_mask_p_addr, self.STATUS_RECIEVE_FIFO_THRESHOLD_FULL | self.STATUS_RECIEVE_FIFO_THRESHOLD_EMPTY)
        
        
        # configure L4 Bus cycle time period
        if self.debug: print("Configuring Fast485 bus cycle time = " + str(self.t_cycle_addr) + " mS")
        self.write_csr(self.t_cycle_addr, self.cycle_time)
                
        
        ### UNCOMMENT WHEN DISCOVERY IS IMPLEMENTED IN L$
        
        # Configure automatic node address discovery (requires features in L4 which do not yet exist (3/28/22)
        #write_csr(DISCOVERY_T1_addr, 0x0006)
        #write_csr(DISCOVERY_T2_addr, 0x0002)
        #write_csr(DISCOVERY_T3_addr, 0x0001)
        #write_csr(DISCOVERY_T4_addr, 0x0008)
        #write_csr(T_HEARTBEAT_addr,  0x000A)
        
        # Start automatic node address discovery
        #write_csr(self.cmd_addr, self.CMD_CLEAR_OP)
        #write_csr(cmd_addr,              CMD_DISCOVERY)
        #sleep(0.025) # discovery should be done within 25mS
        
        #disc_complete = False
        #disc_start_time = time.time()
        #while time.time() < disc_start_time + 0.025:  # time out after 25 millisecond if we haven't seen DISCOVERY command complete
        #    if self.read_csr(self.status_addr) & 0x01 == 0x01
        #        disc_complete = True
        #        break
        #if not disc_complete: 
        #    sys.exit("Error: Fast485 Discovery didn't complete.")
        
        
        # clear Command register and set the command and analyzer pointers to beginning (lowest address) of the RAM
        self.clear()
        
        # start the 485 interface running
        self.start()
        
        # wait for evidence that the first transaction has been sent 
        # this watches the bus analyzer to see that its pointer has incremented to the seconda transaction position
        
        self.start_time = time.time()
        while time.time() < self.start_time + 1:  # time out after 1 second if we haven't seen a transaction yet
            if self.an_pointer_addr >= 4:
                self.fast485_running = True
                if self.debug: print("Fast485 is running.")
                break
        if not self.fast485_running: 
            sys.exit("Error: Fast485 IP didn't start.")
        
            
    def init_command_ram(self):
        ## set first transaction location in command ram to the status_request command
        get_sts_frame = self.HostFrame()
            
        ## do this if we want the nodes to respond to get status all the time
        ## comment it out if we don't want the nodes to respond unless explicitly requested
        if self.always_send_get_status:
            for i in range(self.max_l4_count):
                print(get_sts_frame.node_segment_dicts[i])
                get_sts_frame.node_segment_dicts[i]["nodeID"] = i + 1
                print(get_sts_frame.node_segment_dicts[i])
        
        # now put the get-status frame into the magic position at offset 0 where FPGA looks for the default transaction
        self.write_frames_to_command_ram(0, get_sts_frame)
        
        
    def write_frames_to_command_ram(self, position, *frames):
        offset = position * self.host_frame_segment_length
        for frame in frames:
            raw_frame = frame.raw_frame()
            for word in raw_frame:
                self.write_cmd_ram(offset, word)
                offset = offset + 4
                  

    def send_from_command_ram(self, num_frames=1, position=1, first_serial_id=None):
        if first_serial_id is not None:
            self.running_serial_id = first_serial_id
        
        for i in range(position, num_frames + position, 1):
            offset = self.host_frame_segment_length * i
            fifo_value = (offset // 4) + (self.running_serial_id << 16)
            if self.debug: print(f"Sending frame at command ram position {i:0d}, offset 0x{offset:04X}, ID 0x{self.running_serial_id:04X}: {fifo_value:08X}") 
            self.fpga_write32(self.base_address + self.fifo_cmd_addr, fifo_value)
            # below is used to verify the contents of the transaction in command ram that is being sent
            #if self.debug: 
            #    print("Sent:")
            #    for cram_offset in range(offset, self.host_frame_segment_length + offset, 4):
            #        print(f"   {self.read_cmd_ram(cram_offset):08X}")
                
            if self.running_serial_id == 0xFFFF:
                self.running_serial_id = 0
            else:
                self.running_serial_id += 1
                
            
    def cmd_ram_debug_loader(self):
        #for transaction in range(8192//16//self.max_l4_count): fill in entire command ram with its own 4-byte aligned address plus node IDs
        if self.debug: print("Loading Command RAM with FIFO address location for debugging.")
        for transaction in range(1, 1120//16//self.max_l4_count):
            tx_base = (transaction * self.max_l4_count * 16)
            for node in range(self.max_l4_count):
                node_base = tx_base + (node * 16)
                self.write_cmd_ram(node_base + 0x0, node + 1 | (0x1 << 8) | (0x2 << 16))
                self.write_cmd_ram(node_base + 0x4, node_base + 0x4)
                self.write_cmd_ram(node_base + 0x8, node_base + 0x8)
                self.write_cmd_ram(node_base + 0xC, node_base + 0xC)
        
    def dump_cmd_ram(self):
        #for transaction in range(8192//16//self.max_l4_count): read out entire command ram
        if self.debug: print("Reading Command RAM:")
        for transaction in range(1120//16//self.max_l4_count):
            if self.debug: print("##### Transaction #" + str(transaction))
            tx_base = (transaction * self.max_l4_count * 16)
            for node in range(self.max_l4_count):
                if self.debug: print("\t##### Node #" + str(node))
                node_base = tx_base + (node * 16)
                print("\t" + f"0x{self.read_cmd_ram(node_base + 0x0):08X}")
                print("\t" + f"0x{self.read_cmd_ram(node_base + 0x4):08X}")
                print("\t" + f"0x{self.read_cmd_ram(node_base + 0x8):08X}")
                print("\t" + f"0x{self.read_cmd_ram(node_base + 0xC):08X}")


    def analyzer_ram_reader(self):
        #for record in range(1024): read out entire command ram
        if self.debug: print("Reading Analyzer RAM:")
        for record in range(1024):
            print(f"##### Record #{record:4.0f}:  ", end='')
            print(f"0x{self.read_ananlyzer_ram(record * 8):08X}", end='')
            print(f"  0x{self.read_ananlyzer_ram((record * 8) + 4):08X}")    
     
    
    def poll_for_responses(self):
        # Since we don't have interrupts working yet, lets just always poll for responses
        if self.debug: print("Starting response poller")
        response_count = 0
        timer = time.time()
        while not self.response_thread_kill: 
            if self.response_thread_enable:
                raw_response = [0]*4
                # wait for status to say FIFO is above full threashold
                if self.read_csr(self.status_addr, silent=True) & self.STATUS_RECIEVE_FIFO_THRESHOLD_FULL:
                #if self.fpga_read32(self.base_address + self.status_addr, silent=True) & self.STATUS_RECIEVE_FIFO_THRESHOLD_FULL:
                    if self.debug: print("FIFO_THRESHOLD_FULL received")
                    
                    for i in range(3, -1, -1):
                        #if self.read_csr(self.status_addr) & self.STATUS_RECIEVE_FIFO_EMPTY:
                        #    print("Tried to read from empty Response FIFO")
                        #    i += 1
                        #    continue
                        #else:
                        raw_response[i] = self.read_csr(self.fifo_resp_addr)
                        #raw_response[i] = self.fpga_read32(self.base_address + self.fifo_resp_addr)
                            
                    response = self.NodeResponse(raw_response[3], raw_response[2], raw_response[1], raw_response[0])
                    
                    response_count += 1
                    if response_count >= 1000:
                        print("Receiving responses at " + str(1000/(time.time() - timer)) + " Hz")
                        response_count = 0
                        timer = time.time()
                
                    # Is this a response to a command we sent, or just a status response? If the later, drop it.
                    #if self.debug and (response.serial_id != 0): response.print_response()
                    if response.node_id != 0: response.print_response()
                    #if self.debug: response.print_response()
                            
                        
                    
        if self.debug: print("Response Poller shut down")
        
        
    def exit_handler(self):
        print('L4_Bus Driver Exiting')
        self.response_thread_kill = True
        self.response_thread.join()
        print('L4_Bus Driver Done')
        sys.exit(0)
        
        
        
        
    
    class HostFrame:
        def __init__(self, node_count=DEFAULT_NODE_COUNT, *node_segments):
            self.node_count = node_count
            self.node_segment_dicts = []
            for i in range(self.node_count):
                try:
                    self.node_segment_dicts.append(node_segments[i])
                except:
                    self.node_segment_dicts.append({"nodeID":0,"commandID":0,"deviceID":0,"arg0":0,"arg1":0,"arg2":0,})
            
        def swap32(self, i):
            return(struct.unpack("<I", struct.pack(">I", i))[0])
        
        def raw_frame(self):     
            # make sure we know how many nodes are on the bus...
            # don't just assume its the number of frames we've collected
            if self.node_count == 0: return(-1)
                
            this_raw_frame = []
            for segment in self.node_segment_dicts:
                # Lets see if the command was passed at all
                try:
                    this_command = segment["commandID"]
                except:
                    this_command = 0
                
                # was it passed as a string identifier or a raw int identifier 
                try:
                    # try to look up the string identifier 
                    command = L4_COMMAND_CODES[this_command].value
                except:
                    # wasn't a valid string, lets see if its at least an integrer
                    if type(this_command) == int:
                        command = this_command
                    else:
                        return(-1)
                
                # Lets see if the device was passed at all
                try:
                    this_device = segment["deviceID"]
                except:
                    this_device = 0
                
                # was it passed as a string identifier or a raw int identifier 
                try:
                    # try to look up the string identifier 
                    device = L4_DEVICE_IDS[this_device].value
                except:
                    # wasn't a valid string, lets see if its at least an integrer
                    if type(this_device) == int:
                        device = this_device
                    else:
                        return(-1)
                        
                # make sure we have valid node ID number and arguments
                try:
                    nodeID = segment["nodeID"]
                    if type(nodeID) != int: return(-1)
                except:
                    nodeID = 0
                    
                try:
                    arg0 = segment["arg0"]
                    if type(arg0) != int: return(-1)
                    #arg0 = self.swap32(arg0)
                except:
                    arg0 = 0
                try:
                    arg1 = segment["arg1"]
                    if type(arg1) != int: return(-1)
                    #arg1 = self.swap32(arg1)
                except:
                    arg1 = 0
                try:
                    arg2 = segment["arg2"]
                    if type(arg2) != int: return(-1)
                    #arg2 = self.swap32(arg2)
                except:
                    arg2 = 0
                
            
                # now build the raw frames
                word0 = nodeID & 0xFF
                word0 += (device & 0xFF) << 8
                word0 += (command & 0xFF) << 16
                this_raw_frame.append(word0) 
                this_raw_frame.append(arg0 & 0xFFFFFFFF)
                this_raw_frame.append(arg1 & 0xFFFFFFFF)
                this_raw_frame.append(arg2 & 0xFFFFFFFF)
            return(this_raw_frame)
                
            
    
    class NodeResponse:
        def __init__(self, word0, word1, word2, word3):
            self.status = word0 & 0x000000FF
            self.serial_id = (word0 & 0x00FFFF00) >> 8
            self.node_id = (word0 & 0xFF000000) >> 24
            self.data0 = word1
            self.data1 = word2
            self.data2 = word3
           
        def print_response(self):
            print("Node Response Received:")
            print(f"   NodeID:\t0x{self.node_id:02X}")
            print(f"   SerialID:\t0x{self.serial_id:04X}")
            try:
                decoded_status = L4_STATUS_CODES(self.status).name
            except:
                decoded_status = f"0x{self.status:02X}"
            print(f"   Status:\t" + decoded_status)
            print(f"   Data[0]:\t0x{self.data0:08X}")
            print(f"   Data[1]:\t0x{self.data1:08X}")
            print(f"   Data[2]:\t0x{self.data2:08X}")