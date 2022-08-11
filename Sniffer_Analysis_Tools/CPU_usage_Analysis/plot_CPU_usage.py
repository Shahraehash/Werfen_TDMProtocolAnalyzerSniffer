from importlib.resources import path
import matplotlib.pyplot as plt
import csv, argparse

def get_data_from_csv(path):
    data = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            data += [row]
    
    result = []
    for elem in data[0]:
        if float(elem) != 0.0:
            result += [float(elem)]
    
    return result


def plot(x, y1, label1, y2, label2, xlabel, ylabel, title):
    plt.plot(x, y1, label = label1)
    plt.plot(x, y2, label = label2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.legend()
    plt.savefig(title)

def main():
    path_file1 = ""
    path_file2 = ""
    title = ""

    parser = argparse.ArgumentParser()
    parser.add_argument("-f1", "--file1", type=str, help = "path for file 1")
    parser.add_argument("-f2", "--file2", type=str, help = "path for file 2")
    parser.add_argument("-t", "--title", type=str, help = "title of the comparison image")
    args = parser.parse_args()

    if args.file1 != None:
        path_file1 = args.file1
    if args.file2 != None:
        path_file2 = args.file2
    if args.title != None:
        title = args.title

    if path_file1 == "" or path_file2 == "":
        raise Exception("One or more paths were not given")

    data1 = get_data_from_csv(path_file1)
    data2 = get_data_from_csv(path_file2)

    x_axis = [float(i) for i in range(max(len(data1),len(data2)))]

    plot(x_axis, data1, path_file1.split('/')[-1], data2, path_file2.split('/')[-1], "iterations", "CPU usage (%)", title)
    plt.clf()


main()