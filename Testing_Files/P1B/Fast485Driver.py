import L4BusDriver
import atexit
        
def send(frame):
    l4_bus.write_frames_to_command_ram(1, frame)
    l4_bus.send_from_command_ram()

def move(node, steps):
    move_rel_frame = l4_bus.HostFrame()
    move_rel_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_movrel', 'deviceID': 'DEVICE_motor', 'arg0': 0x766D6772, 'arg1': steps, 'arg2': 0}
    send(move_rel_frame)

def abort(node):
    abort_frame = l4_bus.HostFrame()
    abort_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_abort', 'deviceID': 'DEVICE_motor', 'arg0': 0, 'arg1': 0, 'arg2': 0}
    send(abort_frame)
    
def get_status(node):
    get_status_frame = l4_bus.HostFrame()
    get_status_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_status_get', 'deviceID': 'DEVICE_board', 'arg0': 0, 'arg1': 0, 'arg2': 0}
    send(get_status_frame)

def get_ver(node):
    get_ver_frame = l4_bus.HostFrame()
    get_ver_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_getver', 'deviceID': 'DEVICE_board', 'arg0': 0, 'arg1': 0, 'arg2': 0}
    send(get_ver_frame)




if __name__ == "__main__":
    l4_bus = L4BusDriver.L4BusDriver(debug=True)
    atexit.register(l4_bus.exit_handler)   

