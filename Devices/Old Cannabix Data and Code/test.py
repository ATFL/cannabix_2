import sys
import datetime
from pathlib import Path
import os
import _thread
import RPi.GPIO as GPIO
import time
import numpy as np
import time
import Adafruit_ADS1x15
from numpy import genfromtxt
import math

R = 10000
V0 = 5

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 2 / 3

## Global variable that will be used for starting and stopping the "getSample" action
continueTest = False
# Variable Declarations
sensor_input_channel_1 = 2 # Pin on ADC used to read analog signal from first sensor in dual channel sensor
sensor_input_channel_2 = 1 # Pin on ADC used to read analog signal from second sensor in dual channel sensor
linear_actuator_position_channel = 0 # Pin on ADC used to read analog signal from linear actuator internal position sensor

pumping_time = 2 # time allowed for vacuum pump to draw sample air
flow_stabilization_time = 2 # time allowed for air to settle after vacuum pump is shut off
sensing_delay_time = 90 # time delay after beginning data acquisition till when the sensor is exposed to sample
sensing_retract_time = 50 # time allowed before sensor is retracted, no longer exposed to sample
duration_of_signal = 20 # time allowed for data acquisition per test run

#pumping_time = 20 # time allowed for vacuum pump to draw sample air
#flow_stabilization_time = 2 # time allowed for air to settle after vacuum pump is shut off
#sensing_delay_time = 9 # time delay after beginning data acquisition till when the sensor is exposed to sample
#sensing_retract_time = 50 # time allowed before sensor is retracted, no longer exposed to sample
#duration_of_signal = 200 # time allowed for data acquisition per test run
extended_state = 2.6 # voltage value achieved when linear actuator is extended to correct sensing depth
retracted_state = 1.5 # voltage value achieved when linear actuator is retracted to idle state
sampling_time = 0.1 # time between samples taken, determines sampling frequency
printing_time = 1

#------------------------Pin definitions------------------------#
# Pin Definitions:
vacuum_pump = 17 # Broadcom pin 17 (P1 pin 11)
linear_actuator_extend = 22 # Broadcom pin 5 (P1 pin 13)
linear_actuator_unlock_retract = 27 # Broadcom pin 12 (P1 pin 15)

#---------------------------------------------------------------------#
# Pin Setup:
GPIO.setmode(GPIO.BCM)    # There are two options for this, but just use the board one for now. Don't worry much about it, we can check the definitions when I get back
GPIO.setup(vacuum_pump, GPIO.OUT) # Specifies vacuum_pump pin as an output
GPIO.setup(linear_actuator_extend, GPIO.OUT) # Specifies linear_actuator_extend pin as an output
GPIO.setup(linear_actuator_unlock_retract, GPIO.OUT) # Specifies linear_actuator_unlock_retract pin as an output

# Initial state for outputs:
GPIO.output(vacuum_pump, GPIO.LOW)
GPIO.output(linear_actuator_extend, GPIO.LOW)
GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)
conversion_value = (adc.read_adc(linear_actuator_position_channel,gain=GAIN)/pow(2, 15))*6.144

if (conversion_value < 4):
    while (conversion_value < 4):
        conversion_value = (adc.read_adc(linear_actuator_position_channel,gain=GAIN)/pow(2, 15))*6.144
        GPIO.output(linear_actuator_extend, GPIO.HIGH)
        print(adc.read_adc(sensor_input_channel_1,gain=GAIN))
GPIO.output(linear_actuator_extend, GPIO.LOW)
if (conversion_value > 1.6):
    while (conversion_value > 1.6):
        conversion_value = (adc.read_adc(linear_actuator_position_channel,gain=GAIN)/pow(2, 15))*6.144
        GPIO.output(linear_actuator_unlock_retract, GPIO.HIGH)
        print(adc.read_adc(sensor_input_channel_1))
GPIO.output(linear_actuator_unlock_retract, GPIO.LOW)

GPIO.cleanup()