#packages
from PyQt5.QtWidgets import QApplication
import argparse, os, sys

#python scripts
import GUI


def run_app(argument, number):
    app = QApplication([argument])

    app_window = GUI.MainWindow(number_of_L4s = number)
    app_window.show()
    app.exec_()


def close_session():
    os._exit(os.EX_OK)


if __name__ == "__main__":
    arg_number_of_L4s = "7"
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int, help="number of L4 boards connected")
    args = parser.parse_args()
    if args.number != None:
        arg_number_of_L4s = args.number

    run_app(sys.argv[0], arg_number_of_L4s)








