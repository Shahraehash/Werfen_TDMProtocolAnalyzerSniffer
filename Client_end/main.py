#packages
from PyQt5.QtWidgets import QApplication
import argparse, os, sys, threading

#python scripts
import GUI

#import recieving_client, sending_client


def run_app(argument, version, number):
    app = QApplication([argument])

    app_window = GUI.MainWindow(version_of_board = version, number_of_L4s = number)
    app_window.show()
    app.exec_()

    '''
    HOST = "192.168.0.1"

    print("Starting Clients...")
    sending_client_thread = threading.Thread(target = sending_client.main, args = (HOST, version, number))
    sending_client_thread.start()

    recieving_client_thread = threading.Thread(target = recieving_client.main, args = (HOST,))
    recieving_client_thread.start()
    '''




def close_session():
    os._exit(os.EX_OK)





if __name__ == "__main__":
    arg_version_of_board = "p1b"
    arg_number_of_L4s = "7"
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", choices={"p1a", "p1b"}, help="version of the L3 boards used")
    parser.add_argument("-n", "--number", type=int, help="number of L4 boards connected")
    args = parser.parse_args()
    if args.version != None:
        arg_version_of_board = args.version
    if args.number != None:
        arg_number_of_L4s = args.number

    run_app(sys.argv[0], arg_version_of_board, arg_number_of_L4s)







