import csv, psutil, time 

def main():
    
    print("Started CPU tracking")
    start_time = time.time()
    pids = []
    #cpu_processes = []
    for process in psutil.process_iter():
        if '/home/pi/scripts/GUI_for_TDMprotocolAnalyzer/Server_end/main.py' in process.cmdline():
            pids += [process.pid]
   
    #print(pid_processes)
    cpu_data = [[0.0]]*len(pids)
    #print(cpu_data)
    for _ in range(100):
        for idx, pid in enumerate(pids):
            #print(len(cpu_data), idx)
            cpu_data[idx] += [psutil.Process(pid).cpu_percent(interval=1)]
    
    #print(cpu_data)
    print("Finished CPU tracking. Took ", str(time.time()-start_time), " seconds.")
    #df = pandas.DataFrame(cpu_data, columns = cpu_processes)
    #df.to_csv("CPU_usage/CPU_usage_recent", sep = ",")
    with open('/home/pi/scripts/GUI_for_TDMprotocolAnalyzer/Server_end/CPU_usage/CPU_usage_P1B.csv', 'w') as f:
        writer = csv.writer(f)
        for row in cpu_data:
            writer.writerow(row)
    
main()
        
