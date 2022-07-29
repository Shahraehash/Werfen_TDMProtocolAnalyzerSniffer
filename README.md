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

- A GUI should show up on your screen. Press the green run button to start the sniffer and packets will display on your screen. 
- If you wish to stop seeing packets, press the red stop button. You can still restart viewing packets by pressing the green run button again. If you wish to complete quit using the sniffer, click the red 'X' button on the top right of the screen. 

*************************************************************************************************************************************************************************************************************************************
Features of the Sniffer:

- Save/Open
    - To save all packets that are sniffed across one use of the GUI, press the save button and you will be prompted to give a file name for the file which will then be saved in a .csv file. 
    - To open a previously saved set of packets, press the open button and select the .csv file that corresponds to the file you wish to open. 

- Filtering: 
    - If at any point you wish to filter the packets you see on your screen, press the headers displayed for each column to choose which values in the column to filter by. 
    - If you'd rather type in a filter, choose by which column in the top left of the screen and type in the value by which you wish to filter the packets by. 

- Hide Status-Get Messages:
    - The L3 board consistently sends status get messages to the L4 boards to make sure it can communicate with the L4 board across the bus. To see these messages uncheck the "hide status-get" checkbox. Otherwise the default setting is to hide these messages.

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
- For P1B:
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


