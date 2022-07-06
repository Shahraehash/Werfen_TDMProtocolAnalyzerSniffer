import console, raw_bus

timeout = 2.0

def move(node, steps):
    l4_bus.Send(int(node), 3, 34, timeout, "rgmv", int(steps))

def abort(node):
    l4_bus.Send(int(node), 3, 37, timeout)

def get_status(node):
    l4_bus.Send(int(node), 1, 0, timeout)

def get_ver(node):
    l4_bus.Send(int(node), 1, 1, timeout)



if __name__ == "__main__":
    console.Console.host = console.BoardHosts.SAMPLE.value
    console.Console.connect()
    l4_bus = raw_bus.RawBus()
    

    