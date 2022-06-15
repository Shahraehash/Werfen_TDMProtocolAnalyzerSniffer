from PyQt5.QtWidgets import QApplication
import sys
import argparse
import os
import GUI

version_of_board = "p1b"
number_of_L4s = 7


def run_app(argument, version, number):
    app = QApplication([argument])
    version_of_board = version
    number_of_L4s = number
    app_window = GUI.MainWindow()
    app_window.show()
    app.exec_()


if __name__ == "__main__":
    arg_version_of_board = ""
    arg_number_of_L4s = ""
    '''
    arg_help = "{0} -v <version of board> -n <number of L4 boards>".format(sys.argv[0])
    try: 
        opts, args = getopt.getopt(sys.argv[1:], "h:v:n:", ["help", "version=", "number="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)
            sys.exit(2)
        elif opt in ("-v", "--version"):
            arg_version_of_board = arg 
        elif opt in ("-n", "--number"):
            arg_number_of_L4s = arg 
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", choices={"p1a", "p1b"}, help="version of the L3 boards used")
    parser.add_argument("-n", "--number", type=int, help="number of L4 boards connected")
    args = parser.parse_args()
    if args.version != "":
        arg_version_of_board = args.version
    if args.number != "":
        arg_number_of_L4s = args.number

    run_app(sys.argv[0], arg_version_of_board, arg_number_of_L4s)


def close_session():
    os._exit(os.EX_OK)
