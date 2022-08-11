import csv, psutil, time, argparse

def main():
    
    name_of_file = ""
    parser = argparse.ArgumentParser()
    parser.add_argument("-o","--output", type=str, help="name of output file")
    args = parser.parse_args()
    if args.output != None:
        name_of_file = args.output

    if name_of_file == "":
        raise Exception("No file name provided. Please try again and provide a file name")


    print("Started CPU tracking")
    start_time = time.time()
    pids = []
    for process in psutil.process_iter():
        if '/home/pi/scripts/GUI_for_TDMprotocolAnalyzer/Server_end/main.py' in process.cmdline():
            pids += [process.pid]
   
    cpu_data = [[0.0]]*len(pids)
    for _ in range(100):
        for idx, pid in enumerate(pids):
            cpu_data[idx] += [psutil.Process(pid).cpu_percent(interval=1)]
    
    print("Finished CPU tracking. Took ", str(time.time()-start_time), " seconds.")
    with open(name_of_file, 'w') as f:
        writer = csv.writer(f)
        for row in cpu_data:
            writer.writerow(row)
    
main()
        
