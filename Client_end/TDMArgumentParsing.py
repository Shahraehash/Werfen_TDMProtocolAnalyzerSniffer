import binascii, struct

Host_Frame_Argument_Types = {"DEVICE_board": {'COMMAND_getver': "", 'COMMAND_setloopback':""},
                  "DEVICE_protocol": {'COMMAND_status_get': "", 'COMMAND_ack_completion': "", 'COMMAND_data_plus': ""},
                  "DEVICE_fault_source":{'COMMAND_genflt': "u", 'COMMAND_clrflt': ""},
                  "DEVICE_event":{'COMMAND_startdef': "", 'COMMAND_enddef': "", 'COMMAND_idxinc': "", 'COMMAND_genevt': "", 'COMMAND_hndlevt': "umm"},
                  "DEVICE_motor":{'COMMAND_enable': "d", 'COMMAND_movabs': "cd", 'COMMAND_movrel': "cd", 'COMMAND_change': "c", 'COMMAND_stop': "c", 'COMMAND_abort': "",
                                  'COMMAND_setpos': "d", 'COMMAND_getpos': "", 'COMMAND_setrpw': "u", 'COMMAND_getrpw': "", 'COMMAND_sethpw': "u", 'COMMAND_gethpw': "",
                                  'COMMAND_setreg': "uu", 'COMMAND_getreg': "u", 'COMMAND_encmon': "u", 'COMMAND_setdump': "", 'COMMAND_setprof': "ccu", 'COMMAND_getprof': "cc",
                                  'COMMAND_sclprof': "cf", 'COMMAND_evtrec': "u", 'COMMAND_sethdel': "d", 'COMMAND_gethdel': "", 'COMMAND_setidel': "d", 'COMMAND_getidel': "",
                                  'COMMAND_settlr': "d", 'COMMAND_gettlr': "", 'COMMAND_movinf': "cd", 'COMMAND_movevt': "d", 'COMMAND_setscaling': "dd", 'COMMAND_getscaling': ""},
                  "DEVICE_sensor": {'COMMAND_read': ""},
                  "DEVICE_binary_output": {'COMMAND_setbit': "d", 'COMMAND_getbit': "", 'COMMAND_readbit': "", 'COMMAND_sqwave': "uu", 'COMMAND_hfwave': "uu", 'COMMAND_testmode1': "", 'COMMAND_testmode2': ""},
                  "DEVICE_pwm": {'COMMAND_setpwm': "uu", 'COMMAND_getpwm': "", 'COMMAND_setpol': "u", 'COMMAND_pwmen': "u"},
                  "DEVICE_adc": {'COMMAND_readadc': "", 'COMMAND_streamadc': "d", 'COMMAND_adcdata': ""},
                  "DEVICE_heater_adc":{'COMMAND_setpgabypass': "u", 'COMMAND_setgainlevel': "u", 'COMMAND_setinputmax': "u", 'COMMAND_setburnoutsources': "u", 'COMMAND_settemperaturesensormode': "u",
                                       'COMMAND_setoperatingmode': "u", 'COMMAND_setdatarate': "u", 'COMMAND_setidaccurrent': "u", 'COMMAND_setpowerswitchconfig': "u", 'COMMAND_setfirfilter': "u", 
                                       'COMMAND_setvoltagereference': "u", 'COMMAND_readheateradc': "u", 'COMMAND_readadcconfig': "", 'COMMAND_startadc': "", 'COMMAND_stopadc': ""},
                  "DEVICE_lld": {'COMMAND_setfq': "d", 'COMMAND_getfq': "", 'COMMAND_setsmpl': "d", 'COMMAND_getsmpl': "", 'COMMAND_setthresh': "f", 'COMMAND_getthresh': "", 'COMMAND_startsns': "",
                                 'COMMAND_endsns': "", 'COMMAND_readlt': "", 'COMMAND_readvals': "", 'COMMAND_setavg': "d", 'COMMAN_getavg': ""},
                  "DEVICE_therm": {'COMMAND_readtmpr': "", 'COMMAND_settcal': "fd", 'COMMAND_gettcal': ""},
                  "DEVICE_heater_ctl": {'COMMAND_pidenable': "df", 'COMMAND_setpidmode': "d", 'COMMAND_getpidmode': "d", 'COMMAND_setpidparam': "df", 'COMMAND_getpidparam': "d", 'COMMAND_getpidvar': "d",
                                        'CCOMMAND_setpidout': "f"},
                  "DEVICE_tachometer": {'COMMAND_readrpm': ""},
                  "DEVICE_rfid": {'COMMAND_rfidenable': "d", 'COMMAND_rfidflags': "", 'COMMAND_gettaglen': "u", 'COMMAND_gettagdata': "u", 'COMMAND_settagread': "u"}}


Node_Frame_Argument_Types = {"DEVICE_board": {'COMMAND_getver': "uuu", 'COMMAND_setloopback':""},
                  "DEVICE_protocol": {'COMMAND_status_get': "", 'COMMAND_ack_completion': "", 'COMMAND_data_plus': ""},
                  "DEVICE_fault_source":{'COMMAND_genflt': "", 'COMMAND_clrflt': ""},
                  "DEVICE_event":{'COMMAND_startdef': "", 'COMMAND_enddef': "", 'COMMAND_idxinc': "", 'COMMAND_genevt': "", 'COMMAND_hndlevt': ""},
                  "DEVICE_motor":{'COMMAND_enable': "", 'COMMAND_movabs': "dd", 'COMMAND_movrel': "dd", 'COMMAND_change': "", 'COMMAND_stop': "", 'COMMAND_abort': "",
                                  'COMMAND_setpos': "", 'COMMAND_getpos': "ddd", 'COMMAND_setrpw': "", 'COMMAND_getrpw': "u", 'COMMAND_sethpw': "", 'COMMAND_gethpw': "u",
                                  'COMMAND_setreg': "", 'COMMAND_getreg': "x", 'COMMAND_encmon': "", 'COMMAND_setdump': "", 'COMMAND_setprof': "", 'COMMAND_getprof': "u",
                                  'COMMAND_sclprof': "", 'COMMAND_evtrec': "d", 'COMMAND_sethdel': "", 'COMMAND_gethdel': "d", 'COMMAND_setidel': "", 'COMMAND_getidel': "d",
                                  'COMMAND_settlr': "", 'COMMAND_gettlr': "d", 'COMMAND_movinf': "dd", 'COMMAND_movevt': "dd", 'COMMAND_setscaling': "", 'COMMAND_getscaling': "dd"},
                  "DEVICE_sensor": {'COMMAND_read': "d"},
                  "DEVICE_binary_output": {'COMMAND_setbit': "", 'COMMAND_getbit': "d", 'COMMAND_readbit': "d", 'COMMAND_sqwave': "", 'COMMAND_hfwave': "", 'COMMAND_testmode1': "", 'COMMAND_testmode2': ""},
                  "DEVICE_pwm": {'COMMAND_setpwm': "", 'COMMAND_getpwm': "uu", 'COMMAND_setpol': "", 'COMMAND_pwmen': ""},
                  "DEVICE_adc": {'COMMAND_readadc': "d", 'COMMAND_streamadc': "", 'COMMAND_adcdata': "d"},
                  "DEVICE_heater_adc":{'COMMAND_setpgabypass': "", 'COMMAND_setgainlevel': "", 'COMMAND_setinputmax': "", 'COMMAND_setburnoutsources': "", 'COMMAND_settemperaturesensormode': "",
                                       'COMMAND_setoperatingmode': "", 'COMMAND_setdatarate': "", 'COMMAND_setidaccurrent': "", 'COMMAND_setpowerswitchconfig': "", 'COMMAND_setfirfilter': "", 
                                       'COMMAND_setvoltagereference': "", 'COMMAND_readheateradc': "d", 'COMMAND_readadcconfig': "ddd", 'COMMAND_startadc': "", 'COMMAND_stopadc': ""},
                  "DEVICE_lld": {'COMMAND_setfq': "", 'COMMAND_getfq': "d", 'COMMAND_setsmpl': "", 'COMMAND_getsmpl': "d", 'COMMAND_setthresh': "", 'COMMAND_getthresh': "f", 'COMMAND_startsns': "",
                                 'COMMAND_endsns': "", 'COMMAND_readlt': "d", 'COMMAND_readvals': "fff", 'COMMAND_setavg': "", 'COMMAN_getavg': "d"},
                  "DEVICE_therm": {'COMMAND_readtmpr': "f", 'COMMAND_settcal': "", 'COMMAND_gettcal': "fd"},
                  "DEVICE_heater_ctl": {'COMMAND_pidenable': "", 'COMMAND_setpidmode': "", 'COMMAND_getpidmode': "", 'COMMAND_setpidparam': "", 'COMMAND_getpidparam': "f", 'COMMAND_getpidvar': "f",
                                        'CCOMMAND_setpidout': ""},
                  "DEVICE_tachometer": {'COMMAND_readrpm': "f"},
                  "DEVICE_rfid": {'COMMAND_rfidenable': "", 'COMMAND_rfidflags': "u", 'COMMAND_gettaglen': "u", 'COMMAND_gettagdata': "uuu", 'COMMAND_settagread': ""}}


def decode_signed_int(arg):
    return str(int(arg, 16))

def decode_unsigned_int(arg):
    binary_representation_arg = binascii.unhexlify(arg)
    return str(int.from_bytes(binary_representation_arg, byteorder= 'little'))

def decode_IEEE_float(arg):
    value = ""
    for i in range(4):
        partition = arg[2*i,2*(i+1)]
        float_value = binascii.unhexlify(partition) + b'\x00\x00'
        value += str(struct.unpack('f', float_value)[0])
    return value
    
def decode_4CC(arg):
    value = ""
    for i in range(4):
        partition = arg[2*i:2*(i+1)]
        int_of_partition = int(partition, 16)
        value += chr(int_of_partition)
    return value[::-1]


def decode_hexadecimal(arg):
    return hex(arg)


def decoding_arguments(dictionary_type, row_value):
    arguments = ""
    #print(row_value['Argument 0'], row_value['Argument 0'][-9:-1])
    #print(bytes(row_value['Argument 0'][-9:-1], 'utf-8'))
    args = [bytes(row_value['Argument 0'][-9:-1], 'utf-8'), bytes(row_value['Argument 1'][-9:-1], 'utf-8'), bytes(row_value['Argument 2'][-9:-1], 'utf-8')]
    #print(args)
    type_for_all_args = dictionary_type[str(row_value['Device'])][str(row_value['Command'])]
    #print(type_for_all_args)
    for index in range(len(type_for_all_args)):
        arguments += " "
        type_arg = type_for_all_args[index]
        if type_arg == 'd':
            arguments += decode_signed_int(args[index])
        elif type_arg == 'u':
            arguments += decode_unsigned_int(args[index])
        elif type_arg == 'f':
            arguments += decode_IEEE_float(args[index])
        elif type_arg == 'c':
            arguments += decode_4CC(args[index])
        elif type_arg == 'x':
            arguments += decode_hexadecimal(args[index]) 
        
    return arguments