from console import Console

class RawBus():
    start_string = "bus485 raw "

    @staticmethod
    def ConstructMessage(node: int, device: int, cmd: int, *args: int):
        """ Construct the bus message string to send """
        res = RawBus.start_string + f'{node} {device} {cmd}'
        for param in args:
            res += " " + str(param)
        return res.strip()

    @staticmethod
    def Send(node: int, device: int, cmd: int, timeout: float, *args: int):
        """ Sends a command and waits for a response """
        Console.clear_buffer()
        Console.write_line(RawBus.ConstructMessage(node, device, cmd, *args))
        return Console.read_line(timeout_seconds=timeout)

    @staticmethod
    def Write(node: int, device: int, cmd: int, *args: int):
        """ Sends a command formatted as a raw bus command """
        Console.write_line(RawBus.ConstructMessage(node, device, cmd, args))


