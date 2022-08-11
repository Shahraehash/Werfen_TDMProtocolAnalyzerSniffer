from tkinter import E
from importlib_metadata import version
import pandas as pd
import argparse

from yaml import SafeLoader
import comparison_algorithms, data_decoding


def compare_packets(shorter_packets, longer_packets):
    list_of_comparison = []
    for elem1 in longer_packets:
        host_frame1 = elem1[0]
        node_frame1 = elem1[1]
        for elem2 in shorter_packets:
            host_frame2 = elem2[0]
            node_frame2 = elem2[1]

            if host_frame1 != [] and host_frame2 != []:
                max_score, align_frame1, align_frame2 = comparison_algorithms.global_alignment(host_frame1, host_frame2, -100)
                list_of_comparison += [['Host Frame', host_frame1, host_frame2, comparison_algorithms.differences_between_frames(host_frame1, host_frame2), align_frame1, align_frame2, max_score]]
            
            if node_frame1 != [] and node_frame2 != []:
                max_score, align_frame1, align_frame2 = comparison_algorithms.global_alignment(node_frame1, node_frame2, -100)
                list_of_comparison += [['Node Frame', node_frame1, node_frame2, comparison_algorithms.differences_between_frames(node_frame1, node_frame2), align_frame1, align_frame2, max_score]]

    return list_of_comparison


def save_dataframe(lst, csv_path, headers):
    df = pd.DataFrame(lst, columns = headers)
    df.to_csv(csv_path, sep = ",")


def main():
    headers = ['Packet Frame', 'Sniffer Frame', 'Rasp Pi Frame', 'Number of Differences', 'Aligned Sniffer Frame', 'Aligned Rasp Pi Frame', 'Max Score of Global Alignment']

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", type=str, help = "version of firmware")
    parser.add_argument("-f1", "--file1", type=str, help = "path for TDMprotocolAnalyzer Sniffer")
    parser.add_argument("-f2", "--file2", type=str, help = "path for Salaea Sniffer")
    parser.add_argument("-o", "--output", type=str, help = "path for Output csv file")
    args = parser.parse_args()

    version_of_firmware = ""
    tdm_sniffer_path = ""
    saleae_sniffer_path = ""
    output_path = ""

    if args.version != None:
        version_of_firmware = args.version
    if args.file1 != None:
        tdm_sniffer_path = args.file1
    if args.file2 != None:
        saleae_sniffer_path = args.file2
    if args.output != None:
        output_path = args.output

    if version_of_firmware == "":
        raise Exception("Version of Firmware was not provided. Please try again with a version provided")
    if tdm_sniffer_path == "" or saleae_sniffer_path == "" or output_path == "":
        raise Exception("One or more of the required paths weren't provied. Please try again with the correct format")
    
    rasp_pi_packets = data_decoding.interpret_rasp_pi_data(tdm_sniffer_path, version_of_firmware)
    saleae_packets = data_decoding.interpret_sniffer_data(saleae_sniffer_path, version_of_firmware)
    comparison_of_packets = compare_packets(rasp_pi_packets, saleae_packets)
    save_dataframe(comparison_of_packets, output_path, headers)
    

    return

main()