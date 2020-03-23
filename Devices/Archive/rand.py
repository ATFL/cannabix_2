# This program is designed to automate the data collection process for the ATFL HETEK Project.
# Developed by Matthew Barriault and Isaac Alexander

# Imports
import RPi.GPIO as GPIO
import time
import piplates.DAQC2plate as DAQC
import numpy as np
from pathlib import Path
import datetime
import os
import Adafruit_DHT


##10 for 1-5%
##methaneConcList = [1000,480,960,1440,1920,2400,2880,3360,3840,4320,4800,475,950,1425,1900,2375,2850,3325,3800,4275,4750,1000,485,970,1455,1940,2425,2910,3395,3880,4365,4850,490,980,1470,1960,2450,2940,3430,3920,4410,4900,495,990,1485,1980,2475,2970,3465,3960,4455,4950,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,1000,2134,1482,4627,1936,3404,2112,1467,4580,1916,3370,2091,1452,4534,1897,3335,2069,1437,4488,1877,3301,2048,1422,4441,1858,3267,2027,1407,4395,1839,3233,1982,1304,2387,730,559,1962,1291,2363,723,553,1942,1278,2339,715,548,1923,1265,2315,708,542,1903,1252,2292,701,537,1883,1239,2268,694,531]
##ethaneConcList = [100,20,40,60,80,100,120,140,160,180,200,25,50,75,100,125,150,175,200,225,250,100,15,30,45,60,75,90,105,120,135,150,10,20,30,40,50,60,70,80,90,100,5,10,15,20,25,30,35,40,45,50,0,0,0,0,0,0,0,0,0,0,100,0,0,0,0,0,21,15,46,19,34,43,30,93,39,68,64,44,139,58,102,85,59,185,77,136,107,74,231,97,170,0,0,0,0,0,20,13,24,7,6,40,26,48,15,11,59,39,72,22,17,79,52,95,29,22,99,65,119,37,28]

if len(methaneConcList) != len(ethaneConcList):
print ("Error! Concentration lists are not the same length!")

numtests = len(methaneConcList)

#------------------------Variable Declarations------------------------#

sensor = Adafruit_DHT.DHT22
humidity_pin = 6

daqc_address = 0 # Assume address if DAQC is set to 0, standard setting
sensor_input_channel_1 = 0 # The physical terminal on DAQCplate the sensor number 1 signal is connected to
sensor_input_channel_2 = 1 # The physical terminal on DAQCplate the sensor number 2 signal is connected to
linear_actuator_position_channel = 2 # The physical terminal on DAQCplate the linear actuator position sensor signal is connected to

# Following correction factors were provided by MKS (MFC Manufacturer) (Ph. 978-284-4000)
methane_correction_factor = 0.72 # Manufacturer specified 10 SCCM Nitrogen is equivalent to 7.2 SCCM Methane through the MFC
ethane_correction_factor = 0.5 # Manufacturer specified 10 SCCM Nitrogen is equivalent to 5 SCCM Ethane through the MFC

##methane_flow_rate = 10  # mL/min, this will be the arbitrary, constant setpoint of the MFC
##ethane_flow_rate = 1
methane_flow_rate = 10
ethane_flow_rate = 1
diffusion_time = 30
# time allowed for injected gas to diffuse in sensing chamber before sensor exposure occurs
mfc_flow_stabilization_time = 5 # venting flow through MFC for 5 seconds while flow stabilizes. Stable flow is then switch into chamber
switching_time = 1 # time allowed for flow and pressure to stabilize within system while switching purge solenoids
sensing_delay_time = 170 # time delay after beginning data acquisition till when the sensor is exposed to sample
sensing_retract_time = 210# time allowed before sensor is retracted, no longer exposed to sample
##sensing_delay_time = 1 # time delay after beginning data acquisition till when the sensor is exposed to sample
##sensing_retract_time = 5 # time allowed before sensor is retracted, no longer exposed to sample
compressed_air_flush_time = 200 # time allowed for compressed air flushing of sensing chamber in seconds
temperature_stabilization_time = 00 #time alowed for the temp fot=r the new compressed air in the chamber to reach the environmental chamber temp
duration_of_signal = 360 # time allowed for data acquisition per test run
extended_state = 3.6 # N35
##extended_state = 2.1 # double
retracted_state = 1.1 # voltage value achieved when linear actuator is retracted to idle state
##extended_state = 3.7 # voltage value achieved when linear actuator is extended to correct sensing depth
##retracted_state = 2.5 # voltage value achieved when linear actuator is retracted to idle state
sampling_time = 0.1 # time between samples taken, determines sampling frequency
printing_time = 1

#------------------------Pin definitions------------------------#
##GPIO.cleanup()
# Pin definitions are BCM
valve_1 = 24
valve_2 = 26
valve_3 = 17
valve_4 = 19
valve_5 = 6
valve_6 = 13
valve_7 = 4
valve_8 = 21

# Pin Definitions:
##methane_valve = valve_6
##ethane_valve = valve_5
##compressed_air_valve = valve_7
##chamber_venting_valve = valve_3
##mfc1_output_to_chamber_valve = valve_2
##mfc2_output_to_chamber_valve = valve_1
##mfc1_venting_valve = valve_4
##mfc2_venting_valve = valve_8

methane_valve = valve_6
ethane_valve = valve_5
compressed_air_valve = valve_7
chamber_venting_valve = valve_3
mfc1_output_to_chamber_valve = valve_1
mfc2_output_to_chamber_valve = valve_2
mfc1_venting_valve = valve_8
mfc2_venting_valve = valve_4

linear_actuator_extend = 5
linear_actuator_unlock_retract = 12

#---------------------------------------------------------------------#

# Pin Setup:
GPIO.setmode(GPIO.BCM)    # There are two options for this, but just use the board one for now. Don't worry much about it, we can check the definitions when I get back
GPIO.setup(methane_valve, GPIO.OUT) # Specifies methane_valve pin as an output
GPIO.setup(ethane_valve, GPIO.OUT) # Specifies ethane_valve pin as an output
GPIO.setup(compressed_air_valve, GPIO.OUT) # Specifies mfc_output_to_chamber_valve pin as an output
GPIO.setup(chamber_venting_valve, GPIO.OUT) # Specifies linear_actuator_extend pin as an output
GPIO.setup(mfc1_output_to_chamber_valve, GPIO.OUT) # Specifies linear_actuator_unlock_retract pin as an output
GPIO.setup(mfc2_output_to_chamber_valve, GPIO.OUT) # Specifies compressed_air_valve pin as an output
GPIO.setup(mfc1_venting_valve, GPIO.OUT) # Specifies chamber_venting_valve pin as an output
GPIO.setup(mfc2_venting_valve, GPIO.OUT) # Specifies mfc_venting_valve pin as an output
GPIO.setup(linear_actuator_extend, GPIO.OUT) # Specifies chamber_venting_valve pin as an output
GPIO.setup(linear_actuator_unlock_retract, GPIO.OUT) # Specifies mfc_venting_valve pin as an output

# Initial state for outputs:
GPIO.output(methane_valve, GPIO.LOW)
GPIO.output(ethane_valve, GPIO.LOW)
GPIO.output(compressed_air_valve, GPIO.LOW)
GPIO.output(chamber_venting_valve, GPIO.LOW)
GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
GPIO.output(mfc1_venting_valve, GPIO.LOW)
GPIO.output(mfc2_venting_valve, GPIO.LOW)
GPIO.output(linear_actuator_extend, GPIO.LOW)
GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)


#------------------------Function definitions------------------------#

def exposeAndCollectData():

    GPIO.output(methane_valve, GPIO.LOW)
    GPIO.output(ethane_valve, GPIO.LOW)
    GPIO.output(compressed_air_valve, GPIO.LOW)
    GPIO.output(chamber_venting_valve, GPIO.LOW)
    GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
    GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
    GPIO.output(mfc1_venting_valve, GPIO.LOW)
    GPIO.output(mfc2_venting_valve, GPIO.LOW)

    start_time = time.time() # capture the time at which the test began. All time values can use start_time as a reference
    dataVector1 = [] # data values to be returned from sensor 1
    dataVector2 = [] # data values to be returned from sensor 2
    tempDataVector = []
    humidityDataVector = []
    timeVector = [] # time values associated with data values
    sampling_time_index = 1 #sampling_time_index is used to ensure that sampling takes place every interval of sampling_time, without drifting.
    data_date_and_time = time.asctime( time.localtime(time.time()) )
    print("Starting data capture")

    while (time.time() < (start_time + duration_of_signal)): # While time is less than duration of logged file


        if (time.time() > (start_time + (sampling_time * sampling_time_index))): # if time since last sample is more than the sampling time, take another sample
            dataVector1.append( DAQC.getADC(daqc_address, sensor_input_channel_1) ) # Perform analog to digital function, reading voltage from first sensor channel
            dataVector2.append( DAQC.getADC(daqc_address, sensor_input_channel_2) ) #  Perform analog to digital function, reading voltage from second sensor channel

            timeVector.append( time.time() - start_time )
            sampling_time_index += 1 # increment sampling_time_index to set awaited time for next data sample
            if ((sampling_time_index - 1) % 10 == 0):
                print(int(time.time() - start_time))

                print(DAQC.getADC(daqc_address, linear_actuator_position_channel))

        # If time is between 10-50 seconds and the Linear Actuator position sensor signal from DAQCplate indicates a retracted state, extend the sensor
##        elif (time.time() >= (start_time + sensing_delay_time) and time.time() <= (sensing_retract_time + start_time) and DAQC.getADC(daqc_address, linear_actuator_position_channel) < extended_state ):
        elif (time.time() >= (start_time + sensing_delay_time) and time.time() <= (start_time + sensing_delay_time + 10) ):

                GPIO.output(linear_actuator_extend, GPIO.HIGH) # Actuate linear actuator to extended position
                GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)# Energizing both control wires causes linear actuator to extend

        # If time is less than 10 seconds or greater than 50 seconds and linear actuator position sensor signal from DAQCplate indicates an extended state, retract the sensor
        elif ( ((time.time() < (sensing_delay_time + start_time)) or (time.time() > (sensing_retract_time + start_time)) ) and DAQC.getADC(daqc_address, linear_actuator_position_channel) > retracted_state):
##        elif ( ((time.time() < (sensing_retract_time + start_time + 10)) and (time.time() > (sensing_retract_time + start_time)) )):
                GPIO.output(linear_actuator_unlock_retract, GPIO.HIGH) # Retract linear actuator to initial position. Energizing only the linear_actuator_unlock_retract wire causes the lineaer actuator to retract
                GPIO.output(linear_actuator_extend, GPIO.LOW)

        # Otherwise, keep outputs off        else:
                GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)
                GPIO.output(linear_actuator_extend, GPIO.LOW)
##                print("blep")

    return dataVector1, dataVector2, timeVector


def inject_methane(injection_conc):
print('Injecting methane')
injection_amount = injection_conc / 500 # mL
injection_time = ( 60 * ( 1 / methane_correction_factor ) * injection_amount ) / methane_flow_rate  # Time in seconds
print ("Methane injection time is " + str(injection_time))

# The "try" and "except" statements dictate what the program does if an error occurs
try:
            # Methane Gas injection:
            GPIO.output(methane_valve, GPIO.HIGH) # Open solenoid valve controlling Methane flow from cylinder
            print(" methane_valve on")

            GPIO.output(mfc1_venting_valve, GPIO.HIGH) # Open solenoid valve venting flow from the MFC to atmosphere
            print(" mfc1_venting_valve on")
##
            time.sleep(mfc_flow_stabilization_time)

            GPIO.output(mfc1_venting_valve, GPIO.LOW) # Close solenoid valve venting flow from MFC to atmosphere
            print(" mfc1_venting_valve off")

            GPIO.output(mfc1_output_to_chamber_valve, GPIO.HIGH) # Open solenoid valve controlling flow from MFC into chamber
            print(" mfc1_output_to_chamber_valve on")


            time.sleep(injection_time) # Wait for appropriate injection time

            GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
            GPIO.output(methane_valve, GPIO.LOW)
            print(" mfc1_output_to_chamber_valve off")

except: # This is what happens if any errors occur:
            print("Something's wrong!")


def inject_ethane(injection_conc):
    print('Injecting ethane')
    injection_amount = injection_conc / 500 # mL
    injection_time = ( 60 * ( 1 / ethane_correction_factor ) * injection_amount ) / ethane_flow_rate  # Time in seconds
    print ("Ethane injection time is " + str(injection_time))

    # The "try" and "except" statements dictate what the program does if an error occurs
    try:
        GPIO.output(ethane_valve, GPIO.HIGH) # Open solenoid valve controlling Methane flow from cylinder
        print(" ethane_valve on")

        GPIO.output(mfc2_venting_valve, GPIO.HIGH) # Open solenoid valve venting flow from the MFC to atmosphere
        print(" mfc2_venting_valve on")
##
        time.sleep(mfc_flow_stabilization_time)

        GPIO.output(mfc2_venting_valve, GPIO.LOW) # Close solenoid valve venting flow from MFC to atmosphere
        print(" mfc2_venting_valve off")

        GPIO.output(mfc2_output_to_chamber_valve, GPIO.HIGH) # Open solenoid valve controlling flow from MFC into chamber
        print(" mfc2_output_to_chamber_valve on")


        time.sleep(injection_time) # Wait for appropriate injection time

        GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
        print(" mfc2_output_to_chamber_valve off")
        GPIO.output(ethane_valve, GPIO.LOW) # Open solenoid valve controlling Methane flow from cylinder
        print(" ethane_valve off")

    except: # This is what happens if any errors occur:
        print("Something's wrong!")

##def inject_methane_and_ethane(methane_injection_conc, ethane_injection_conc):
##    inject_methane(methane_injection_conc)
##    inject_ethane(ethane_injection_conc)

def inject_methane_and_ethane(methane_injection_conc, ethane_injection_conc):
    print('Injecting methane and ethane')
    methane_injection_amount = methane_injection_conc / 500 # mL
    ethane_injection_amount = ethane_injection_conc / 500 # mL

    methane_injection_time = ( 60 * ( 1 / methane_correction_factor ) * methane_injection_amount ) / methane_flow_rate  # Time in seconds
    ethane_injection_time = ( 60 * ( 1 / ethane_correction_factor ) * ethane_injection_amount ) / ethane_flow_rate  # Time in seconds

    print ("Methane injection time is " + str(methane_injection_time))
    print ("Ethane injection time is " + str(ethane_injection_time))

    # The "try" and "except" statements dictate what the program does if an error occurs
    try:
        # Initial state for outputs:
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(mfc1_venting_valve, GPIO.LOW)
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(mfc2_venting_valve, GPIO.LOW)

        # Methane Gas injection:
        GPIO.output(methane_valve, GPIO.HIGH) # Open solenoid valve controlling Methane flow from cylinder
        print(" methane_valve on")
        GPIO.output(mfc1_venting_valve, GPIO.HIGH) # Open solenoid valve venting flow from the MFC to atmosphere
        print(" mfc1_venting_valve on")
        GPIO.output(ethane_valve, GPIO.HIGH) # Open solenoid valve controlling Ethane flow from cylinder
        print(" ethane_valve on")
        GPIO.output(mfc2_venting_valve, GPIO.HIGH) # Open solenoid valve venting flow from the MFC to atmosphere
        print(" mfc2_venting_valve on")

        time.sleep(mfc_flow_stabilization_time) # Vent flow through MFC to stablize flow rate

        GPIO.output(mfc1_venting_valve, GPIO.LOW) # Close solenoid valve venting flow from MFC to atmosphere
        print(" mfc1_venting_valve off")
        PIO.output(mfc1_output_to_chamber_valve, GPIO.HIGH) # Open solenoid valve controlling flow from MFC into chamber
        print(" mfc1_output_to_chamber_valve on")
        time.sleep( methane_injection_time )
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
        print(" mfc1_output_to_chamber_valve off")
        GPIO.output(methane_valve, GPIO.LOW) # Open solenoid valve controlling Methane flow from cylinder
        print(" methane_valve off")

        GPIO.output(mfc2_venting_valve, GPIO.LOW) # Close solenoid valve venting flow from MFC to atmosphere
        print(" mfc2_venting_valve off")
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.HIGH) # Open solenoid valve controlling flow from MFC into chamber
        print(" mfc2_output_to_chamber_valve on")
        time.sleep( ethane_injection_time )
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
        print(" mfc2_output_to_chamber_valve off")
        GPIO.output(ethane_valve, GPIO.LOW) # Open solenoid valve controlling Methane flow from cylinder
        print(" ethane_valve off")

##        if methane_injection_time > ethane_injection_time:
##
##            print("sleeping " + str(ethane_injection_time) + " seconds")
##            time.sleep( ethane_injection_time )
##
##            GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
##            print(" mfc2_output_to_chamber_valve off")
##
##            print("sleeping " + str(methane_injection_time - ethane_injection_time) + " seconds")
##            time.sleep( methane_injection_time - ethane_injection_time )
##
##            GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
##            print(" mfc1_output_to_chamber_valve off")
##
##
##        elif ethane_injection_time > methane_injection_time:
##            print("sleeping " + str(methane_injection_time) + " seconds")
##            time.sleep( methane_injection_time )
##
##            GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
##            print(" mfc1_output_to_chamber_valve off")
##
##            print("sleeping " + str(ethane_injection_time - methane_injection_time) + " seconds")
##            time.sleep( ethane_injection_time - methane_injection_time )
##
##
##            GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
##            print(" mfc2_output_to_chamber_valve off")
##
##
##        elif methane_injection_time == ethane_injection_time:
##            print("sleeping " + str(methane_injection_time) + " seconds")
##            time.sleep( methane_injection_time )
##
##            GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
##            print(" mfc1_output_to_chamber_valve off")
##
##            GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW) # Close solenoid valve controlling flow from MFC into chamber
##            print(" mfc2_output_to_chamber_valve off")

##        else:
##            print("WAT")

##        GPIO.output(methane_valve, GPIO.LOW) # Open solenoid valve controlling Methane flow from cylinder
##        print(" methane_valve off")
##        GPIO.output(ethane_valve, GPIO.LOW) # Open solenoid valve controlling Ethane flow from cylinder
##        print(" ethane_valve off")

    except: # This is what happens if any errors occur:
        print("Something's wrong!")

def pre_inject_methane():
    print('pre-injecting methane')
    # The "try" and "except" statements dictate what the program does if an error occurs
    try:
        # Initial state for outputs:
        GPIO.output(methane_valve, GPIO.HIGH)
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.HIGH)
        GPIO.output(chamber_venting_valve, GPIO.HIGH)

##        print("time to pre inject")
        time.sleep(30)

        GPIO.output(methane_valve, GPIO.LOW)
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(chamber_venting_valve, GPIO.LOW)

    except: # This is what happens if any errors occur:
        print  ("Something's wrong!")

def pre_inject_ethane():
    print('pre-injecting ethane')
    # The "try" and "except" statements dictate what the program does if an error occurs
    try:
        # Initial state for outputs:
        GPIO.output(ethane_valve, GPIO.HIGH)
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.HIGH)
        GPIO.output(chamber_venting_valve, GPIO.HIGH)

##        print("time to pre inject")
        time.sleep(30)

        GPIO.output(ethane_valve, GPIO.LOW)
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(chamber_venting_valve, GPIO.LOW)

    except: # This is what happens if any errors occur:
        print  ("Something's wrong!")


def pre_inject_methane_and_ethane():
    print('pre-injecting methane and ethane')
    # The "try" and "except" statements dictate what the program does if an error occurs
    try:
        GPIO.output(ethane_valve, GPIO.HIGH)
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.HIGH)
        GPIO.output(methane_valve, GPIO.HIGH)
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.HIGH)
        GPIO.output(chamber_venting_valve, GPIO.HIGH)

        time.sleep(30)

        GPIO.output(methane_valve, GPIO.LOW)
        GPIO.output(ethane_valve, GPIO.LOW)
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(chamber_venting_valve, GPIO.LOW)

    except: # This is what happens if any errors occur:
            print("Something's wrong!")


def purgeChamber():
    print("Purging chamber")
    # Flush chamber with compressed air
    try:
        # Initial state for outputs:
        GPIO.output(methane_valve, GPIO.LOW)
        GPIO.output(ethane_valve, GPIO.LOW)
        GPIO.output(compressed_air_valve, GPIO.LOW)
        GPIO.output(chamber_venting_valve, GPIO.LOW)
        GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
        GPIO.output(mfc1_venting_valve, GPIO.LOW)
        GPIO.output(mfc2_venting_valve, GPIO.LOW)

        GPIO.output(chamber_venting_valve, GPIO.HIGH) # Open solenoid valve for compressed air venting
        time.sleep(0.5)
        GPIO.output(compressed_air_valve, GPIO.HIGH) # Open solenoid valve for compressed air from compressor

        time.sleep(compressed_air_flush_time) # Wait for allowed sensing chamber flush time

        GPIO.output(compressed_air_valve, GPIO.LOW) # Close solenoid valve for compressed air from compressor
        time.sleep(1)
        # time.sleep(switching_time) # Allow flow/pressure to stabilize for duration of switching_time
        GPIO.output(chamber_venting_valve, GPIO.LOW) # Close solenoid valve for compressed air venting

    except: # This is what happens if any errors occur:
        print("Something's wrong!")


def createFolders(year, month, day):
    ##  Get the path for the folders by year, month and day
    year_path = '/home/pi/Documents/HETEK_Automation_System_Verification_Results/' + str(year)
    year_folder = Path(year_path)
    month_path = '/home/pi/Documents/HETEK_Automation_System_Verification_Results/' + str(year) + '/' +str(month)
    month_folder = Path(month_path)
    day_path = '/home/pi/Documents/HETEK_Automation_System_Verification_Results/' + str(year) + '/' +str(month) + '/' + str(day)
    day_folder = Path(day_path)
    ##  Start creating the folders, when the var complete == True, all the folders have been created
    complete = False
    while complete == False:
        if year_folder.is_dir():
            if month_folder.is_dir():
                if day_folder.is_dir():
                    print ("Today's folder is ready")
                    complete = True
                else:
                    os.makedirs(day_path)
                    print ("Creating today's folder")
                    complete = True
            else:
                os.makedirs(month_path)
        else:
            os.makedirs(year_path)

    ## This function gets the current time for the time stamp of the txt file and for the folder location

#------------------------Main operation-------------------------------#

##time.sleep(1800)
##try:
for i in range(numtests):

    # Do pre-injections
##    if ethaneConcList[i] != 0 and methaneConcList[i] != 0:
##        pre_inject_methane_and_ethane()
##    elif methaneConcList[i] != 0:
##        pre_inject_methane()
##    elif ethaneConcList[i] != 0:
##        pre_inject_ethane()

    purgeChamber()
    print ("Purging done. Waiting for gas to cool")
    time.sleep(temperature_stabilization_time)

    # Do injections
    if ethaneConcList[i] != 0 and methaneConcList[i] != 0:
##        inject_methane_and_ethane( methaneConcList[i], ethaneConcList[i] )
        inject_methane( methaneConcList[i] )
        inject_ethane( ethaneConcList[i] )
    elif methaneConcList[i] != 0:
        inject_methane( methaneConcList[i] )
    elif ethaneConcList[i] != 0:
        inject_ethane( ethaneConcList[i] )


##      This block of code will display the time value every 10 seconds during the diffusion period
    start_time = time.time()
    printing_time_index = 0

##while loop will run for the duration of the diffusion_time
    if methaneConcList[i] != 0 or ethaneConcList[i] != 0 :
        while(time.time() < (start_time + diffusion_time) ):
            if(time.time() > (start_time + (printing_time * printing_time_index))):
                printing_time_index += 1 # increment printing_time_index to set time for next print statement
    ##              if printing_time_index is a multiple of 10, print diffusion timer
                if(((printing_time_index - 1) % 150) == 0):
                    print("Diffusion timer: " + str(int(time.time() - start_time)))

    GPIO.output(chamber_venting_valve, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(chamber_venting_valve, GPIO.LOW)

    dataVector1, dataVector2, timeVector = exposeAndCollectData()
    combinedVector = np.column_stack((timeVector, dataVector1, dataVector2))
##    humidity, temperature = Adafruit_DHT.read_retry(sensor, humidity_pin)
##    header = [0,temperature, humidity]
##    combinedVector = np.vstack((header, combinedVector))

    current_time = datetime.datetime.now()
    year = current_time.year
    month = current_time.month
    day = current_time.day
    createFolders(year, month, day)
    hour = current_time.hour
    minute = current_time.minute
    fileName = str(year) + '-' + str(month) + '-' + str(day) + '_' + str(hour) + ':' + str(minute) + ':' + 'Methane:' + str(methaneConcList[i]) + '-' + 'Ethane:' + str(ethaneConcList[i]) + '_N35_env_chamber_room_temp.csv'
    np.savetxt(r'/home/pi/Documents/HETEK_Automation_System_Verification_Results/' + str(year) + '/' + str(month) + '/' + str(day) + '/' + str(fileName), combinedVector, fmt = '%.10f', delimiter = ',')
##    time.sleep(1800)
##        np.savetxt(r'/home/pi/Documents/HETEK_Automation_System_Verification_Results/July_10_Methane'+ str(methaneConcList[i]) + '_' + 'Ethane' + str(ethaneConcList[i]) + '_' + str(data_date_and_time) + '.csv', combinedVector, fmt = '%.10f', delimiter = ',')

##finally:
GPIO.output(methane_valve, GPIO.LOW)
GPIO.output(ethane_valve, GPIO.LOW)
GPIO.output(compressed_air_valve, GPIO.LOW)
GPIO.output(chamber_venting_valve, GPIO.LOW)
GPIO.output(mfc1_output_to_chamber_valve, GPIO.LOW)
GPIO.output(mfc2_output_to_chamber_valve, GPIO.LOW)
GPIO.output(mfc1_venting_valve, GPIO.LOW)
GPIO.output(mfc2_venting_valve, GPIO.LOW)
GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)
GPIO.output(linear_actuator_extend, GPIO.LOW)
print("Executed finally block")
##
GPIO.cleanup()
#------------------------End of Main-------------------------------#
