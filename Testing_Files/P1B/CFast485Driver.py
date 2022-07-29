import L4BusDriver
import multiprocessing, time

#Simulation

def send(l4_bus, frame):
    l4_bus.write_frames_to_command_ram(1, frame)
    l4_bus.send_from_command_ram()

def move(l4_bus, node, steps):
    move_rel_frame = l4_bus.HostFrame()
    move_rel_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_movrel', 'deviceID': 'DEVICE_motor', 'arg0': 0x766D6772, 'arg1': steps, 'arg2': 0}
    send(l4_bus, move_rel_frame)

def abort(l4_bus, node):
    abort_frame = l4_bus.HostFrame()
    abort_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_abort', 'deviceID': 'DEVICE_motor', 'arg0': 0, 'arg1': 0, 'arg2': 0}
    send(l4_bus, abort_frame)
    
def get_status(l4_bus, node):
    get_status_frame = l4_bus.HostFrame()
    get_status_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_status_get', 'deviceID': 'DEVICE_board', 'arg0': 0, 'arg1': 0, 'arg2': 0}
    send(l4_bus, get_status_frame)

def get_ver(l4_bus, node):
    get_ver_frame = l4_bus.HostFrame()
    get_ver_frame.node_segment_dicts[0] = {'nodeID': node, 'commandID': 'COMMAND_getver', 'deviceID': 'DEVICE_board', 'arg0': 0, 'arg1': 0, 'arg2': 0}
    send(l4_bus, get_ver_frame)


def simulation():
    l4_bus = L4BusDriver.L4BusDriver(debug = False)
    num_iteration = 1
    while True:
        if num_iteration % 10 == 0:
            move(l4_bus, 1, 1000)
        else:
            get_status(l4_bus, 1)
        time.sleep(0.03)
        num_iteration += 1

def main():
    p = multiprocessing.Process(target = simulation)
    p.start()
    p.join


if __name__ == "__main__":
    main()