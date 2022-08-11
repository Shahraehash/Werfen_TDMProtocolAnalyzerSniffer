TDM Protocol Analyzer Sniffer

*************************************************************************************************************************************************************************************************************************************

Description: 

On Beacon, there are multiple L3 boards which control varying number of L4 boards. The communication between the L3 host and up to 7 L4 nodes is across a RS-485 bus which is built on a time-division multiplexing (TDM) principle. This means there are packets of data that is exchanged between the L3 board and L4 boards regularly. Each cycle consists of a L3 board sending a fixed packet to specific defined nodes and those nodes later respond with a status packet. This sniffer's goal is to analyze each of the packets that are sent across this bus and report it to the user. 

*************************************************************************************************************************************************************************************************************************************

Getting Started: 

1. Download all of the folders and files in the GUI_for_TDMprotocolAnalyzer/ repository and place it on your PC. Obtain a Raspberry Pi that you can setup as the sniffer. 

2. Setting up the Raspberry Pi:
- Place the folder GUI_for_TDMprotocolAnalyzer/Server_end/ in the home directory of the Raspberry Pi (either through scp or through the SD card)
- Change the IP address of the Raspberry Pi to a static IP address (ex: run "ifconfig 192.168.0.1" in Terminal to set the Raspberry Pi's IP address to 192.168.0.1)
- Edit /etc/rc.local at the end of the file but above "exit 0" to have the following two lines of code
    - "sudo route add -net default gw [static IP address of Raspberry PI]"
    - "sudo python3 [path to main.py file that is in the GUI_for_TDMprotocolAnalyzer/Server_end/ folder placed on Raspberry Pi]"

3. Setting up the Ethernet Connection to the PC:
- Connect an ethernet cable from the Raspberry Pi to the PC
- In the network settings for the ethernet port adjust the TCP/IPv4 so that they match the following:
    - IP address: [at least one byte different than the IP address defined for the Raspberry Pi (ex: 192.168.0.2)]
    - Subnet mask: 255.255.255.0
    - Default gateway: [IP address for the Raspberry Pi (ex: 192.168.0.1)]
- If you are planning on using a VM set the settings of the VM to a bridged NAT configuration
- Ensure that you are able to ping the Raspberry Pi (run "ping [IP address of the Raspberry Pi]" in command prompt)

4. Setting up the GUI on the PC:
- Place the folder GUI_for_TDMprotocolAnalyzer/Client_end/ on your PC
- Once you are in this folder on your PC run "python3 main.py -n [number of L4 boards connected]" in your terminal (default settings are -number_of_L4s = 7). If you need any help with running it run "python3 main.py -h" in terminal
- A GUI should show up on your screen. Press the green run button to start the sniffer and packets (non-status-get) will display on your screen (see hide status-get messages in features of the sniffer for more details). 
- If you wish to stop seeing packets, press the red stop button. You can still restart viewing packets by pressing the green run button again. If you wish to complete quit using the sniffer, click the red 'X' button on the top right of the screen. 
- While running the GUI, keep the terminal prompt open as all exception errors will be displayed there to help you use this tool and analyze why some packets may not be visible on the GUI.

*************************************************************************************************************************************************************************************************************************************

Features of the Sniffer:

- Save/Open
    - To save all packets that are sniffed across one use of the GUI, press the save button and you will be prompted to give a file name for the file which will then be saved in a .csv file. 
    - To open a previously saved set of packets, press the open button and select the .csv file that corresponds to the file you wish to open. 

- Filtering: 
    - If at any point you wish to filter the packets you see on your screen, press the headers displayed for each column to choose which values in the column to filter by. 
    - If you'd rather type in a filter, choose by which column in the top left of the screen and type in the value by which you wish to filter the packets by. 

- Hide Status-Get Messages:
    - The L3 board consistently sends status get messages to the L4 boards to make sure it can communicate with the L4 board across the bus. To see these messages uncheck the "hide status-get" checkbox. Otherwise the default setting is to hide these messages. Note the bus communicates these status-get messages roughly every 2 ms, so there will be a lot of messages accumulated on the GUI.

- Clear Data:
    - In the case you want to clear all of the data that is displayed on the GUI, you can press this button to remove all of the data. Note this data wont be saved unless you save it prior to clearing. This will be most useful after checking if there is any communication occuring between the L3 and L4 board. 

- Summary:
    - As communication is occuring across the bus, decoded raw packets are displayed on the screen. To get a more detailed analysis of any packet, press the packet you wish to learn more about. 
        - You will see an explanation which is a "plain english" explanation of what communication occurred between the L3 board and L4 board including the fact that the arguments are decoded.
        - You will see the raw byte code that corresponds to the packet that is sent. In packets sent by the L3 host, you will see that the byte code is split by each node frame and that only the significant node byte code is actually highlighted in the display. 

*************************************************************************************************************************************************************************************************************************************

Example for Testing: 

Within the GUI_for_TDMprotocolAnalyzer/Testing_Files/ there are some scripts that you can use to run some sample packets across L3 and L4 to test the functionality of the GUI
- For P1A:
    - Connect your PC to your board through an ethernet cable. Configure your network settings for that ethernet port so it has the following settings:
        - IP address: 10.0.3.150
        - Subnet mask: 255.0.0.0
        - Default gateway: 
    - Ensure that you can ping your board (sample: 10.0.3.2; reagent: 10.0.3.3)
    - In GUI_for_TDMprotocolAnalyzer/Testing_Files/P1A there are two files you can run:
        - run "python3 P1A_CFast485_Driver.py" to have continuous packets being sent (every 0.03 second a status-get message is sent for node 1 and every 0.3 second a move motor_rel message is sent to node 1)
        - run "python3 -i P1A_Fast485_Driver.py" to be in interactive mode. Here you can run the following commands where you specify the node number and the steps:
            - move(node, steps)
            - abort(node)
            - get_status(node)
            - get_ver(node)

- For P1B (with the Fast485Driver)
    - Follow the steps on the Confluence page to set up the petalinux environment (https://jira.ilww.com:8099/confluence/display/BCN/L3+VM+Setup+-+P1B). 
    - Once you are connected to your L3 board through a serial terminal (sudo picocom /dev/ttyUSB0 -b115200), on your linux machine navigate to <Project_Root>/beacon_l3/bsp/project-spec/meta-user/recipes-apps/beacon/files and run:
        - scp -r firmware root@192.168.1.100:/usr/bin/beacon
        - scp -r tests root@192.168.1.100:/usr/bin/beacon
    - On the serial terminal window in /usr/bin/beacon/firmware/server/drivers/fast485 run:
        - python3 fast485_service.py &
        - python3 L4CmdShell.py
    - Once you are in this shell you can run move commands as follows:
        - Node: 1
        - Device: 3
        - Command: 34
        - Arg 0: rgmv
        - Arg 1: 10000
        - Arg 2: (leave blank)

- For P1B (without the Fast485Driver)
    - Connect your PC to your board through an ethernet cable. Configure your network settings for that ethernet port so it has the following settings:
        - IP address: 192.168.1.150
        - Subnet mask: 255.0.0.0
        - Default gateway: 
    - Ensure that you can ping your board (192.168.1.100)
    - On the SD card of your board add GUI_for_TDMprotocolAnalyzer/Testing_Files/P1B
    - On your PC run "ssh root@192.168.1.100" with the password as root
    - Within /media/sd-mmcblk0p1/P1B/ you will have two files you can run:
        - run "python3 CFast485_Driver.py" to have continuous packets being sent (every 0.03 second a status-get message is sent for node 1 and every 0.3 second a move motor_rel message is sent to node 1)
        - run "python3 -i Fast485_Driver.py" to be in interactive mode. Here you can run the following commands where you specify the node number and the steps:
            - move(node, steps)
            - abort(node)
            - get_status(node)
            - get_ver(node)

*************************************************************************************************************************************************************************************************************************************

Sniffer Analysis Tools:

Throughout the construction of the sniffer, some specific analysis were performed to determine the performance of the sniffer. In the Sniffer_Analysis_Tools there are two tools that have been developed to help the user to determine how well the sniffer is truly performing. 

- Comparing Serial Packets
    In the comparing-serial-packets-from-sniffers folder there is a tool used to analyze how well this TDMprotocolAnalyzer sniffer performs compared to the Saleae Sniffer. Although the scripts used for this comparison are written and placed in this folder, the data currently found in these txt files are during development of Version 3 of the Sniffer where some packets were not sniffed by the TDMprotocolAnalyzer sniffer. 
        - To run this tool, generate txt files of the serial raw byte code read by both the TDMprotocolAnalyzer sniffer and the Saleae sniffer
        - Within the comparing-serial-packets-from-sniffers folder run:
            - "python3 compare_txtfiles.py -v [version of firmware] -f1 [path of TDMprotocolAnalyzer sniffer txt file] -f2 [path of Saleae sniffer txt file] -o [path of output csv file]"
            - example: "python3 compare_txtfiles.py -v p1a -f1 raspberrypi_txtfiles/P1A_Rasp_Pi_raw_TDM_data.txt -f2 sniffer_txtfiles/P1A_Sniffer_hex_bytes.txt -o comparison_csv_files/P1A_Sniffer_Rasp_Pi.csv"

- Track CPU usage
    One of the concerns along the process was how much CPU usage the Raspberry Pi TDMprotocolAnalyzer sniffer uses since a high CPU usage will slow down the sniffer's ability to send packets to the PC. Therefore to determine the amount of CPU used by the sniffer, a tool was developed to compute how much CPU the sniffer used when running a certain amount of cycles (set to 100 currently) to generate a plot to determine if improvements were made when changing the method for sniffing. 
        - To run this tool, while the TDMprotocolAnalyzer sniffer is running in the background, run "python3 Server_end/Track_CPU_usage/CPUusage_tracker.py -o [path of output file]" which will generate the .csv file of the output. 
        - To then visually compare the csv files, run "python3 Sniffer_Analysis_Tools/CPU_usage_Analysis/plot_CPU_usage.py -f1 [path for one of the csv files (ideally the one you expect to have a higher CPU usage)] -f2 [path for the other csv file] -t [title you want for the figure generated and the name of the image]" 

