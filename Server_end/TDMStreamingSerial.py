import json, queue, serial, time 
import global_vars, TDMProtocolAnalyzer

serial_port_device='/dev/ttyS0'
serial_baud_rate=921600
#serial_timeout=0.000015 # slightly longer than the length of a 921600 byte
#serial_timeout=0.00015
idle_timeout=-1 # timeout in seconds before script gives up waiting for a host frame. -1 is infininte
node_timeout=0.0001 #3 # typically about 260uS from end of host frame to start of first node frame per L4 Bus Protocol Spec
number_of_L4s=None

serial_queue = queue.Queue()

def stream_serial():
    
    length_of_read = 1000 #length of the read can change. (inversely proportional to CPU usage: the greater the value the less CPU usage)
    ser = serial.Serial(
            port = serial_port_device,
            baudrate = serial_baud_rate,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS
            #without a serial timeout, ser.read is a blocking function which waits until it gets the required number of bytes
        )
    
    time.sleep(0.2) # give the port a moment to open
    
    while True:
        try:
            data = ser.read(length_of_read)
        except serial.SerialException as e:
            TDMProtocolAnalyzer.TDM_data_queue.put("No Serial Connection")
        serial_queue.put(data)
        
        

def get_serial_data():
    return serial_queue.get()