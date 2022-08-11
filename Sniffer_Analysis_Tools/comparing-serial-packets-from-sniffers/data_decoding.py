def interpret_rasp_pi_data(rasp_pi_pathname, version):
    with open(rasp_pi_pathname) as f:
        all_TDM_data = f.readlines()
    
    packet_list = []
    for elem in all_TDM_data:
        packet = []
        splitted_elem = elem.split('[')
        Host_Frame_raw = splitted_elem[6].split(",")        
        Host_Frame = []
        for item in Host_Frame_raw[:-1]:
            Host_Frame += [hex(int(item[2:6], 16))]
        
        Node_Frame = []
        if version == "p1a":
            Node_Frame_raw = splitted_elem[11].split(",")
            for item in Node_Frame_raw:
                Node_Frame += [hex(int(item[2:6], 16))]

        packet = [Host_Frame, Node_Frame]
        packet_list += [packet]
    return packet_list

def interpret_sniffer_data(sniffer_pathname, version):
    with open(sniffer_pathname) as f:
        all_sniffer_data = f.readlines()
    
    all_sniffer_string_data = all_sniffer_data[0].replace("\\", "")
    split_sniffer_string_list = []
    string_split = ""
    for char in all_sniffer_string_data:
        string_split += char
        if string_split[-6:] == "xC3xAA":
            split_sniffer_string_list += [string_split[:-6]]
            string_split = string_split[-6:]

    packet_list = []
    for packet in split_sniffer_string_list:
        raw_packet_split = packet.split('FF')
        #print(raw_packet_split)
        Host_Frame_raw = raw_packet_split[0].split('x')
        Node_Frames_raw = raw_packet_split[1:]
        
            
        Host_Frame = []
        for elem in Host_Frame_raw:
            if elem == "":
                continue
            Host_Frame += ["0x"+elem[:2]]
            for rem in elem[2:]:
                Host_Frame += ["0x"+rem]
        
        Node_Frames = []
        if version == "p1a":
            for node in Node_Frames_raw:
                raw_node_frame = node.split('x')
                Node_Frame = []
                for elem in raw_node_frame:
                    if elem == "":
                        continue
                    Node_Frame += ["0x"+elem[:2]]
                    for rem in elem[2:]:
                        Node_Frame += ["0x"+rem]
                Node_Frames += Node_Frame
        
        packet_list += [[Host_Frame, Node_Frames]]
    return packet_list