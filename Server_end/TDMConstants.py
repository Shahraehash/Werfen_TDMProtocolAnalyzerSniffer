from enum import Enum

#define L4_DEVICE_IDS
class L4_DEVICE_IDS(Enum):
    DEVICE_board						    = 0x01  # Board as a whole  - singleton 
    DEVICE_events						    = 0x02  # Event Broker  - singleton 
    DEVICE_motor						    = 0x03  # Motor, one and only per board 
    DEVICE_lld							    = 0x04  # LLD device */
    DEVICE_lld_adc                          = 0x05  # ADC for LLD signal
    DEVICE_probe_adc                        = 0x06  # Probe ADC, only one per heater board
    DEVICE_sleeve_adc                       = 0x07  # Sleeve ADC, only one per heater board
    DEVICE_probe_therm1                     = 0x08  # Probe 1 thermistor
    DEVICE_probe_therm2                     = 0x09  # Probe 2 thermistor
    DEVICE_sleeve_therm1                    = 0x0A  # Sleeve 1 thermistor
    DEVICE_sleeve_therm2                    = 0x0B  # Sleeve 2 thermistor
    DEVICE_slt_sensor_1_in				    = 0x10  # Slot sensor 1 
    DEVICE_slt_sensor_2_in				    = 0x11  # Slot sensor 2 
    DEVICE_slt_sensor_3_in				    = 0x12  # Slot sensor 3 
    DEVICE_sw_1_in						    = 0x13  # DIP switch, pos 0 
    DEVICE_sw_2_in						    = 0x14  # DIP switch, pos 1 
    DEVICE_sw_3_in						    = 0x15  # DIP switch, pos 2 
    DEVICE_sw_4_in						    = 0x16  # DIP switch, pos 3 
    DEVICE_id_1_in						    = 0x17  # Board ID, pos 0 
    DEVICE_id_2_in						    = 0x18  # Board ID, pos 1 
    DEVICE_id_3_in						    = 0x19  # Board ID, pos 2 
    DEVICE_alert_rx_in					    = 0x1A  # Alert line, RX input 
    DEVICE_smc_stall_l_in				    = 0x1B  # drv8711 STALLn signal 
    DEVICE_smc_fault_l_in				    = 0x1C  # drv8711 FAULTn signal 
    DEVICE_smc_int_in					    = 0x1D  # drv8711 VINT signal 
    DEVICE_qec_pa_in					    = 0x1E  # Quadrature decoder, phase A input 
    DEVICE_qec_pb_in					    = 0x1F  # Quadrature decoder, phase B input 
    DEVICE_rs485_rx_in					    = 0x20  # RS485 port, RX input 
    DEVICE_sol_efuse_flt_l_in			    = 0x21  # Solenoid fuse input 
    DEVICE_sol_sense_in				        = 0x22  # Solenoid sensor 
    DEVICE_sleeve_temp_flt_l_in		        = 0x23  #
    DEVICE_sleeve_efuse_flt_l_in		    = 0x24  #
    DEVICE_sleeve_heat_en_out			    = 0x25  #
    DEVICE_upper_sleeve_heat_pwm_l_pwm	    = 0x26  #
    DEVICE_lower_sleeve_heat_pwm_l_pwm	    = 0x27  #
    DEVICE_piercer_flag_in				    = 0x30  # Piercer Flag ID 
    DEVICE_foot_flag_in				        = 0x31  # Foot Flag ID 
    DEVICE_cap_flag_in					    = 0x32  # Cap Flag ID 
    DEVICE_probe_flag_in				    = 0x33  # Probe Flag ID 
    DEVICE_probe_temp_flt_l_in			    = 0x34  #
    DEVICE_probe_efuse_flt_l_in		        = 0x35  #
    DEVICE_probe_heat_en_out			    = 0x36  #
    DEVICE_upper_probe_heat_pwm_l_pwm	    = 0x37  #
    DEVICE_lower_probe_heat_pwm_l_pwm	    = 0x38  #
    DEVICE_smc_scs_out					    = 0x40  # 
    DEVICE_smc_clk_out					    = 0x41  # drv8711 SPI clock 
    DEVICE_rs485_tx_out				        = 0x42  # RS485 port, TX output 
    DEVICE_sol_drv_l_pwm				    = 0x43  # Solenoid control output 
    DEVICE_sda_out						    = 0x44  # SDA of I2C port to EEPROM 
    DEVICE_scl_out						    = 0x45  # SCL of I2C port to EEPROM 
    DEVICE_smc_step_out				        = 0x46  # drv8711 STEP signal 
    DEVICE_smc_mosi_out				        = 0x47  # drv8711 SPI MOSI 
    DEVICE_smc_miso_out				        = 0x48  # drv8711 SPI MISO
    DEVICE_alert_tx_out				        = 0x49  # Alert line, TX output 
    DEVICE_rs485_txe_out				    = 0x4A  # RS485 transmit enable output
    DEVICE_led1_out					        = 0x4B  # LED for developer's use
    DEVICE_led2_out					        = 0x4C  #
    DEVICE_slt_sensor_en_out			    = 0x4D  # Slot sensor enable output
    DEVICE_smc_sleep_l_out				    = 0x4E  # drv8711 SLEEPn signal 
    DEVICE_smc_reset_out				    = 0x4F  # drv8711 RESET signal 
    DEVICE_smc_dir_out					    = 0x50  # drv8711 DIR signal
    DEVICE_smc_bin1_out				        = 0x51  # drv8711 BIN1 signal
    DEVICE_smc_bin2_out				        = 0x52  # drv8711 BIN2 signal
    DEVICE_sol_en_out					    = 0x53  # Solenoid Enable output 
    DEVICE_ee_wp_out					    = 0x54  # 
    DEVICE_fan_en_l_out				        = 0x55  #
    DEVICE_fan1_pwm_pwm				        = 0x56  #
    DEVICE_fan2_pwm_pwm				        = 0x57  #
    DEVICE_eot_sensor_b_in				    = 0x61  #
    DEVICE_cap_sensor_b_in				    = 0x62  #
    DEVICE_spare_12_out				        = 0x63  #
    DEVICE_spare_13_out				        = 0x64  #
    DEVICE_solenoid_efuse_flt_l_in		    = 0x71  #
    DEVICE_solenoid_en_out				    = 0x72  #
    DEVICE_solenoid_drive_l_pwm		        = 0x73  #
    DEVICE_solenoid_sense_in			    = 0x74  #
    DEVICE_upper_probe_heater_pid           = 0x80  #
    DEVICE_lower_probe_heater_pid           = 0x81  #
    DEVICE_upper_sleeve_heater_pid          = 0x82  #
    DEVICE_lower_sleeve_heater_pid          = 0x83  #
    DEVICE_fan1_tachometer                  = 0x84  #
    DEVICE_fan2_tachometer                  = 0x85  #
    DEVICE_gripper_open_out                 = 0x86  #
    DEVICE_gripper_close_out                = 0x87  #
    DEVICE_rfid_reader                      = 0x88  #
    


#define L4_BOARD_COMMANDS
class L4_COMMAND_CODES(Enum):
    #board commands
    COMMAND_getver			= 0x01 	#  get L4 firmware version */)
    COMMAND_getcmdver		= 0x02 	#  get version of command set */)
    COMMAND_setloopback     = 0x0F  #  set board in "loopback" mode */)
    
    #protocol commands
    COMMAND_status_get		= 0x00 	#  no action on L4 */)
    COMMAND_ack_completion	= 0xF0 	#  acknowledge command completion */) 
    COMMAND_data_plus		= 0xF1 	#  request streaming data */)
    
    #Events
    #Event Manager Commands
    COMMAND_startdef		= 0x10  #  start event definition session */) 
    COMMAND_enddef			= 0x11 	#  end event definition session */) 
    COMMAND_idxinc			= 0x17 	#  increment event index */)
    #Event Source Commands
    COMMAND_genevt			= 0x12 	#  tell event source what event to generate */) 
    #Event Handler Commands
    COMMAND_hndlevt		    = 0x15 	#  tell event handler what event to handle */)
    
    #Fault Source Commands
    COMMAND_genflt			= 0x13 	#  tell event source when to generate fault */) 
    COMMAND_clrflt			= 0x14 	#  clear defined faults */) 

    #Motor Commands  
    COMMAND_enable			= 0x20 	#  enable/disable motor */)
    COMMAND_movabs			= 0x21 	#  move absolute (profile, position), return (motpos, encpos) */) 
    COMMAND_movrel			= 0x22 	#  move relative (profile, position), return (motpos, encpos) */) 
    COMMAND_change			= 0x23 	#  change speed using profile */) 
    COMMAND_stop			= 0x24  #  stop using profile (0=current) */) 
    COMMAND_abort			= 0x25 	#  abort */) 
    COMMAND_setpos			= 0x26 	#  set position */) 
    COMMAND_getpos			= 0x27 	#  get position, return (motpos, encpos, encraw) */) 
    COMMAND_setrpw			= 0x28 	#  set run power % */) 
    COMMAND_getrpw			= 0x29 	#  get run power % */) 
    COMMAND_sethpw			= 0x2A 	#  set hold power % */) 
    COMMAND_gethpw			= 0x2B 	#  get hold power % */) 
    COMMAND_setreg			= 0x2C 	#  set register value ?*/) 
    COMMAND_getreg			= 0x2D 	#  get register value ?*/) 
    COMMAND_encmon			= 0x2E 	#  enable/disable encoder monitor (10kHz sampling divider) */) 
    COMMAND_setdump		    = 0x2F 	#  dump */) 
    COMMAND_setprof		    = 0x30 	#  set profile parameter (???) */) 
    COMMAND_getprof		    = 0x31 	#  get profile parameter (???) */) 
    COMMAND_sclprof		    = 0x32 	#  scale profile by specified factor */) 
    COMMAND_evtrec			= 0x33 	#  get position at specified event */) 
    COMMAND_sethdel		    = 0x34 	#  set hold delay in ticks */) 
    COMMAND_gethdel		    = 0x35 	#  get hold delay */) 
    COMMAND_setidel		    = 0x36 	#  set idle delay in ticks */) 
    COMMAND_getidel		    = 0x37 	#  get idle delay */) 
    COMMAND_settlr			= 0x38 	#  set step loss tolerance */) 
    COMMAND_gettlr			= 0x39 	#  get step loss tolerance */) 
    COMMAND_movinf			= 0x3A 	#  move indefinitely (profile, direction (+1/-1)), return (motpos, encpos) */) 
    COMMAND_movevt			= 0x3B 	#  start move on event (event index), return (motpos, encpos) */) 
    COMMAND_setscaling		= 0x3C 	#  set full steps per revolution scale of the motor and and encoder lines per rev */) 
    COMMAND_getscaling		= 0x3D 	#  get full steps per revolution scale of the motor and encoder lines per rev */) 
    
    #Sensor commands
    COMMAND_read			= 0x50 	#  --
    
    #Binary Output Commands
    COMMAND_setbit			= 0x58 	#  set bit value */)
    COMMAND_getbit			= 0x59 	#  get back set bit value */)
    COMMAND_readbit         = 0x5A 	#  read actual pin state of bit output */)
    COMMAND_sqwave			= 0x5B 	#  generate square wave up to 5kHz */)
    COMMAND_hfwave			= 0x5C 	#  generate square wave > 5kHz*/)
    COMMAND_testmode1		= 0x5D 	#  switch to test mode 1 */)
    COMMAND_testmode2		= 0x5E 	#  switch to test mode 2 */)
    
    #PWM Commands
    COMMAND_setpwm			= 0x60 	#  --
    COMMAND_getpwm			= 0x61 	#  --
    COMMAND_setpol			= 0x62 	#  --
    COMMAND_pwmen			= 0x63 	#  --
    
    #ADC Commands
    COMMAND_readadc		    = 0x70 	#  return a single reading */) 
    COMMAND_streamadc		= 0x71 	#  start/stop streaming data */) 
    COMMAND_adcdata		    = 0x72 	#  command code for streamed data */)
    
    #Heater ADC Commands
    COMMAND_setpgabtypass   = 0x80  #  set ADS1120 PGA Bypass setting */)
    COMMAND_setgainlevel    = 0x81  #  set ADS1120 gain level */)
    COMMAND_setinputmax     = 0x82  #  set ADS1120 input multiplexer setting */)
    COMMAND_setburnoutsources = 0x83 #  set ADS1120 burnout sources */)
    COMMAND_settemperaturesensormode = 0x84 #  set ADS1120 temperature sensor mode */)
    COMMAND_setoperatingmode = 0x85 #  set ADS1120 operating mode */)
    COMMAND_setdatarate     = 0x86  #  set ADS1120 data rate */)
    COMMAND_setidaccurrent  = 0x87  #  set ADS1120 IDAC Current */)
    COMMAND_setpowerswitchconfig = 0x88 #  set ADS1120 power switch configuration */)
    COMMAND_setfirfilter    = 0x89  #  set ADS1120 FIR filter setting */)
    COMMAND_setvoltagereference = 0x90 #  set ADS1120 voltage reference setting */)
    COMMAND_readheateradc   = 0x91  #  return last ADC conversion value */)
    COMMAND_readadcconfig   = 0x92  #  return ADC config register value */)
    COMMAND_startadc        = 0x93  #  start ADC conversions */)
    COMMAND_stopadc         = 0x94  #  stop ADC conversions */)
    
    #LLD Commands
    COMMAND_setfq           = 0xA0  #  set excitation frequency */)
    COMMAND_getfq           = 0xA1  #  get excitation frequency */)
    COMMAND_setsmpl         = 0xA2  #  set sampling prescaler */)
    COMMAND_getsmpl         = 0xA3  #  get sampling prescaler */)
    COMMAND_setthresh       = 0xA4  #  set threshold */)
    COMMAND_getthresh       = 0xA5  #  get threshold */)
    COMMAND_startsns        = 0xA6  #  start lld process */)
    COMMAND_endsns          = 0xA7  #  end lld process */)
    COMMAND_readlt          = 0xA8  #  read latch */)
    COMMAND_readvals        = 0xA9  #  read processing values */)
    COMMAND_setavg          = 0xAA  #  set averaging window */)
    COMMAND_getavg          = 0xAB  #  read back averaging window */)
    
    #Therm Commands
    COMMAND_readtmpr        = 0xB0  #  read last temperature */)
    COMMAND_settcal         = 0xB1  #  set calibration values */)
    COMMAND_gettcal         = 0xB2  #  get calibration values */)
    
    #Heater CTL Commands
    COMMAND_pidenable       = 0xB8  #  enable/disable PID control */)
    COMMAND_setpidmode      = 0xB9  #  set PID mode */)
    COMMAND_getpidmode      = 0xBA  #  get PID mode */)
    COMMAND_setpidparam     = 0xBB  #  set selected PID parameter */)
    COMMAND_getpidparam     = 0xBC  #  get selected PID parameter */)
    COMMAND_getpidvar       = 0xBD  #  get selected PID variable */)
    COMMAND_setpidout       = 0xBE  #  set output */)
    
    #Tachometer
    COMMAND_readrpm         = 0xC0  #  read measured RPM */)
    
    #RFID Commands
    COMMAND_rfidenable      = 0xC8  #  enable/disable RFID scanning */)
    COMMAND_rfidflags       = 0xC9  #  read presence flags for all antennas */)
    COMMAND_gettaglen       = 0xCA  #  get data length of requested tag */)
    COMMAND_gettagdata      = 0xCB  #  read data from tag */)
    COMMAND_settagread      = 0xCC  #  mark tag as read */)


# Define L4 Board Response Status Codes
class L4_STATUS_CODES(Enum):
    #Success Status Code
	STATUS_Success = 0x0 #Success */ \
	
	#Command Status Code
	STATUS_CommandExecuting = 0x01 #Command is pending completion */ \
	STATUS_CommandAborted = 0x02 #Command was aborted */ \
	
	#Error Status Code
	STATUS_ErrorInvalidDevice = 0x81 #Invalid device ID in the command */ \
	STATUS_ErrorInvalidCommand = 0x82 #Invalid command */ \
	STATUS_ErrorInvalidArgCount = 0x83 #Invalid number of command arguments */ \
	STATUS_ErrorInvalidArgument = 0x84 #Invalid command argument */ \
	STATUS_ErrorDeviceBusy = 0x85 #Command can't be executed, device is busy */ \
	STATUS_ErrorMotorStepLoss = 0x86 #Step loss detected */ \
	STATUS_ErrorEStop = 0x87 #E-Stop condition is detected */ \
	STATUS_ErrorNotSupported = 0x88 #Function not supported */ \
	STATUS_ErrorResourceNotAvailable = 0x89 #Out of specified resource */ \
	
class IS_IN():
    set_of_DEVICE_ID_values = set(item.value for item in L4_DEVICE_IDS)
    set_of_COMMAND_ID_values = set(item.value for item in L4_COMMAND_CODES)
    set_of_STATUS_CODES_values = set(item.value for item in L4_STATUS_CODES)
    
    def dev_is_in(value):
        return value in IS_IN.set_of_DEVICE_ID_values
    
    def cmd_is_in(value):
        return value in IS_IN.set_of_COMMAND_ID_values
    
    def stat_is_in(value):
        return value in IS_IN.set_of_STATUS_CODES_values