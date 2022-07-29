import string
from Wrapper.node_status import *
from Wrapper.console import Console, BoardHosts
from typing import List
import time
import curses

class BusStatus():
    """ Continuously ping the boards and print output to console, updating on interval """

    def __init__(self, board_type, timeout=0.01, delay=1):
        """
        Bus manager object that can check the state of all nodes on a bus

        @param board_type a known board type, enum: int to iterate over, or list of integers to ping
        @param timeout the time to wait for a response
        @param delay the time wait between responses
        """
        self.board_type = board_type

        if board_type == BoardType.SAMPLE:
            self.nodes = SampleNodes
        elif board_type == BoardType.REAGENT:
            self.nodes = ReagentNodes
        elif issubclass(type(board_type), Enum):
            self.nodes = board_type
        elif isinstance(board_type, List):
            self.nodes = board_type
        else:
            print("failed to identify list of boards to ping")
            assert False

        self.node_map = {}
        for node in self.nodes:
            name = node
            if issubclass(type(node), Enum):
                name = node.name
            self.node_map[name] = L4Node(node, timeout)

        self.timeout = timeout
        self.delay = delay

    def GetAllVersion(self):
        """ An optional request to print out all board versions instead of monitoring status """
        for name in self.node_map:
            version = self.node_map[name].get_board_version()
            print(f"{name} Version: {version}")

    def Execute(self):
        """ The main loop that prints out the status """
        status = {}
        try:
            print("\nstarting up... ")
            i = 0
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()

            while True:
                status = self.GetAllStatus()
                stdscr.addstr(0, 0, f'===  STATUS :: {i}  === ')

                j = 1
                for name in status:
                    stdscr.addstr(j, 0, f'  {name}:')
                    stdscr.addstr(j, 14, f'{status[name].name}')
                    j += 1

                stdscr.refresh()
                time.sleep(self.delay)
                i += 1

        except KeyboardInterrupt:
            pass
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()

            print("final status: ")
            for name in status:
                print(f'  {name}: {status[name].name}')

    def GetAllStatus(self):
        status = {}
        for name in self.node_map:
            status[name] = self.node_map[name].ping_board()
        return status


if __name__ == "__main__":
    import argparse

    cmd = argparse.ArgumentParser(description='Continuously check if the L4 Nodes are Present or Missing')

    #required argument to specify who to ping
    group = cmd.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', '--reagent', help="Use the Reagent Board Configuration", action='store_true')
    group.add_argument('-s', '--sample', help="Use the Sample Board Configuration", action='store_true')
    group.add_argument('-c', '--custom', nargs="+", type=int, help="Use custom list of node IDs (int)")

    # optional arguments
    cmd.add_argument('-t', '--timeout', type=float, nargs='?', const=1, default=0.01, help="Set the timeout used to determine if present")
    cmd.add_argument('-d', '--delay', type=float, nargs='?', const=1, default=1, help="Set the refresh rate of the program")
    cmd.add_argument('-a', '--address', type=str, help="Set the address used by the L3 board")
    cmd.add_argument('-v', '--version', help="Request the versoions of the L4 boards", action='store_true')

    args = cmd.parse_args()

    # set the boards to ping
    board_type = None
    if args.sample:
        board_type = BoardType.SAMPLE
        Console.host = BoardHosts.SAMPLE.value
    elif args.reagent:
        board_type = BoardType.REAGENT
        Console.host = BoardHosts.REAGENT.value
    elif args.custom:
        board_type = args.custom

    # set the address to ping
    if args.address:
        Console.host = args.address

    # connect the console to the CLI port
    Console.print_result = False
    try:
        Console.connect()
    except:
        print("failed to connect to CLI port")
        exit(-1)

    if not Console.is_connected():
        print("failed to connect to CLI port")
        exit(-1)

    status_program = BusStatus(board_type, args.timeout, args.delay)

    #If we just want to print versions once
    if args.version:
        status_program.GetAllVersion()
    else:
        #execute the program
        status_program.Execute()
