import sys
import socket
import select
import time
import atexit
from enum import Enum

global_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

class BoardHosts(Enum):
    SAMPLE = '10.0.3.2'
    REAGENT = '10.0.3.3'
    ORU = '10.0.3.4'
    UNKNOWN = '10.0.3.250' # don't expect results from this

class Console():
    host = BoardHosts.UNKNOWN.value #can be changed by user
    port = 50000
    print_result = False

    def __init__(self):
        Console.connect()

    @staticmethod
    def is_connected():
        """ Verify if the socket is connected to the raw bus """
        try:
            data = ("\r\n").encode('utf-8')
            sent = global_socket.send(data)
            return sent == len(data)
        except:
            return False

    @staticmethod
    def connect():
        """ Connect the console to the CLI socket """
        if not Console.is_connected():
            global_socket.settimeout(3.0)
            global_socket.connect ((Console.host, Console.port))
            global_socket.setblocking(0)
            Console.clear_buffer()
            return Console.is_connected()
        return True

    @staticmethod
    def clear_buffer(tolerance = 1):
        """ clear the CLI socket buffer
        @param tolerance the time used to read from the socket
        """
        while Console.read_line(tolerance)[0]:
            pass

    @staticmethod
    def disconnect():
        """ Disconnect the CLI socket """
        global_socket.close()
        pass

    @staticmethod
    def is_blocking():
        """ Get if the socket is blocking """
        return global_socket.getblocking()

    @staticmethod
    def set_blocking(block):
        """ Set if the socket is blocking """
        global_socket.setblocking(block)
        return global_socket.getblocking()

    @staticmethod
    def read_line(timeout_seconds=None):
        """
        Read a response from the CLI socket

        @param timeout_seconds time to wait for response, otherwise wait forever
        @return (bool, msg) if a message was read and if so, the message received.
        """
        resp = ""
        ch = b' '
        while True:
            ready = select.select([global_socket], [], [], timeout_seconds)
            if ready[0]:
                byte = global_socket.recv (1)
                ch = byte.decode ('utf-8')
                if (ord (ch) == 10):
                    break
                resp = resp + ch
            else:
                if Console.print_result:
                    print ("Timeout waiting for response")
                return (False, "")

        if Console.print_result:
            print (resp)

        return (True, resp)

    @staticmethod
    def write_line(message):
        """
        Write a message to the CLI socket

        @param message the string to write to the CLI socket
        """
        sending = (message+"\r\n").encode('utf-8')
        global_socket.sendall (sending)
