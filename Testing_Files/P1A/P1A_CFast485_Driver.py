import console, raw_bus
import multiprocessing, time

timeout = 0.0

def move(l4_bus, node, steps):
    l4_bus.Send(int(node), 3, 34, timeout, "rgmv", int(steps))

def abort(l4_bus, node):
    l4_bus.Send(int(node), 3, 37, timeout)

def get_status(l4_bus, node):
    l4_bus.Send(int(node), 1, 0, timeout)

def get_ver(l4_bus, node):
    l4_bus.Send(int(node), 1, 1, timeout)



def simulation():
    console.Console.host = console.BoardHosts.SAMPLE.value
    console.Console.connect()
    l4_bus = raw_bus.RawBus()
    num_iteration = 0
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