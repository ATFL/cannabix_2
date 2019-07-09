#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
import sys
import datetime
from pathlib import Path
import os
import _thread
import tkinter.ttk as ttk
import RPi.GPIO as GPIO
import serial
import numpy as np
import time
import Adafruit_ADS1x15
from numpy import genfromtxt
import math

def createFolders(year, month, day):
    ##  Get the path for the folders by year, month and day
    year_path = '/home/pi/Documents/Tests/' + str(year)
    year_folder = Path(year_path)
    month_path = '/home/pi/Documents/Tests/' + str(year) + '/' + str(month)
    month_folder = Path(month_path)
    day_path = '/home/pi/Documents/Tests/' + str(year) + '/' + str(month) + '/' + str(day)
    day_folder = Path(day_path)
    ##  Start creating the folders, when the var complete == True, all the folders have been created
    complete = False
    while complete == False:
        if year_folder.is_dir():
            if month_folder.is_dir():
                if day_folder.is_dir():
                    complete = True
                else:
                    try:
                        print(day_path)
                        original_mask = os.umask(0x0000)
##                        desired_permission = 0777
                        os.makedirs(day_path, mode=0x0777)
                        complete = True
                    finally:
                        os.umask(original_mask)
            else:
                os.makedirs(month_path)
        else:
            os.makedirs(year_path)
            
def ADC_linear_actuator():
    conversion_value = (adc1.read_adc(0,gain=GAIN)/pow(2, 15))*6.144
    return conversion_value

try:
    mult = 10
    ser = serial.Serial("/dev/ttyS0")
    writestring = "M 4\r\n"
    ser.write(writestring.encode())
    writestring = "K 2\r\n"
    ser.write(writestring.encode())
    ser.flushInput()

    R = 10000
    V0 = 5

    # Create an ADS1115 ADC (16-bit) instance.
    adc1 = Adafruit_ADS1x15.ADS1115(0x48)
    #adc2 = Adafruit_ADS1x15.ADS1115(0x49)

    GAIN = 2 / 3

    extended_state = 4.5 # voltage value achieved when linear actuator is extended to correct sensing depth
    retracted_state = 0.9 # voltage value achieved when linear actuator is retracted to idle state
    printing_time = 1
    continueTest = True
    sampling_time = 0.1 # time between samples taken, determines sampling frequency

    sensing_delay_time = 2 # normall 9 time delay after beginning data acquisition till when the sensor is exposed to sample
    sensing_retract_time = 20 # normally 130 time allowed before sensor is retracted, no longer exposed to sample
    duration_of_signal = 20 # normally 300time allowed for data acquisition per test run

    vacuum_pump = 4 # Broadcom pin 17 (P1 pin 11)
    solenoid = 17 # Broadcom pin 17 (P1 pin 11)
    linear_actuator_extend = 27 # Broadcom pin 5 (P1 pin 13)
    linear_actuator_unlock_retract = 22 # Broadcom pin 12 (P1 pin 15)

    linearActuator2 = 18
    GPIO.setmode(GPIO.BCM)    # There are two options for this, but just use the board one for now. Don't worry much about it, we can check the definitions when I get back
    GPIO.setup(vacuum_pump, GPIO.OUT) # Specifies vacuum_pump pin as an output
    GPIO.setup(solenoid, GPIO.OUT) # Specifies vacuum_pump pin as an output
    GPIO.setup(linear_actuator_extend, GPIO.OUT) # Specifies linear_actuator_extend pin as an output
    GPIO.setup(linear_actuator_unlock_retract, GPIO.OUT) # Specifies linear_actuator_unlock_retract pin as an output


    GPIO.setup(linearActuator2, GPIO.OUT)
    pwm = GPIO.PWM(linearActuator2, 50)
    
    '''GPIO.output(linear_actuator_extend, GPIO.LOW)
    GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)'''
    GPIO.output(solenoid, GPIO.LOW)
    GPIO.output(vacuum_pump, GPIO.LOW)

    pwm.start(10)
    global stopCounter
    start_time = time.time()  # capture the time at which the test began. All time values can use start_time as a reference
    dataVector1 = []  # data values to be returned from sensor 1
    dataVector2 = []  # data values to be returned from sensor 2
    dataVector3 = []  # data values to be returned from sensor 1
    dataVector4 = []  # data values to be returned from sensor 2
    timeVector = []  # time values associated with data values
    sampling_time_index = 1  # sampling_time_index is used to ensure that sampling takes place every interval of sampling_time, without drifting.

    print("Starting data capture")

    while (time.time() < (start_time + duration_of_signal)) and (continueTest == True):  # While time is less than duration of logged file
        if (time.time() > (start_time + (
                sampling_time * sampling_time_index)) and (continueTest == True)):  # if time since last sample is more than the sampling time, take another sample
    ##        print("get another sample")
            dataVector1.append(adc1.read_adc(0,
                                            gain=GAIN))  # Perform analog to digital function, reading voltage from first sensor channel
            dataVector2.append(adc1.read_adc(1,
                                            gain=GAIN))  # Perform analog to digital function, reading voltage from second sensor channel
            dataVector3.append(adc1.read_adc(2,
                                            gain=GAIN))  # Perform analog to digital function, reading voltage from first sensor channel
            dataVector4.append(adc1.read_adc(3,
                                            gain=GAIN))  # Perform analog to digital function, reading voltage from second sensor channel
            timeVector.append(time.time() - start_time)
            sampling_time_index += 1
            
    ##        writestring = "Z\r\n"
    ##        ser.write(writestring.encode())
    ##        resp = ser.read(10)
    ##        resp = resp[:8]
    ##        co2 = float(resp[2:])
    ##        print("CO2: " + co2 * mult)
            
    ##        print(ADC_linear_actuator())

            # increment sampling_time_index to set awaited time for next data sample
    ##    if ((sampling_time_index - 1) % 10 == 0):
    ##        print(int(time.time() - start_time))

        # If time is between 10-50 seconds and the Linear Actuator position sensor signal from the ADC indicates a retracted state, extend the sensor
        elif (time.time() >= (start_time + sensing_delay_time) and time.time() <= (
                sensing_retract_time + start_time) and ADC_linear_actuator() < extended_state) and (continueTest == True):
    ##            print("extend actuator")
            pwm.ChangeDutyCycle(13)
            
##            GPIO.output(linear_actuator_extend, GPIO.HIGH)  # Actuate linear actuator to extended position
##            GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)  # Energizing both control wires causes linear actuator to extend

        # If time is less than 10 seconds or greater than 50 seconds and linear actuator position sensor signal from the ADC indicates an extended state, retract the sensor
        elif (((time.time() < (sensing_delay_time + start_time)) or (
                time.time() > (sensing_retract_time + start_time))) and ADC_linear_actuator() > retracted_state) and (continueTest == True):
    ##            print("retract actuator")
            pwm.ChangeDutyCycle(6)
           ## GPIO.output(linear_actuator_unlock_retract,GPIO.HIGH)  # Retract linear actuator to initial position. Energizing only the linear_actuator_unlock_retract wire causes the linear actuator to retract
            ## GPIO.output(linear_actuator_extend, GPIO.LOW)
        # Otherwise, keep outputs off
        else:
            pwm.ChangeDutyCycle(6)
            ## GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)
            ## GPIO.output(linear_actuator_extend, GPIO.LOW)
        
    combinedVector = np.column_stack((timeVector, dataVector1, dataVector2, dataVector3, dataVector4))

    # This section of code is used for generating the output file name. The file name will contain date/time of test, as well as concentration values present during test
    current_time = datetime.datetime.now()
    year = current_time.year
    month = current_time.month
    day = current_time.day
    createFolders(year, month, day)
    hour = current_time.hour
    minute = current_time.minute
    fileName = str(year) + '-' + str(month) + '-' + str(day) + '_' + str(hour) + ':' + str(minute) + 'Mo_Neg_nolid.csv'
    #fileName = str(year) + '-' + str(month) + '-' + str(day) + '_' + str(hour) + ':' + str(minute) + '_bl.csv'
    np.savetxt(r'/home/pi/Documents/Tests/' + str(year) + '/' + str(month) + '/' + str(day) + '/' + str(fileName),
               combinedVector, fmt='%.10f', delimiter=',')

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
    sys.exit(0)

    # The keyboard interrupt only works if you enter control -c into the terminal, all other keystrokes will not quit the function. 
finally:
    pwm.stop()
    GPIO.cleanup()
