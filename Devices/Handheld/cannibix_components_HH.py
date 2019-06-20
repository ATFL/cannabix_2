# -----> RPi Imports <------
import RPi.GPIO as GPIO
import time
import os
#import Adafruit_ADS1x15
import adafruit_ads1x15.ads1115 as ADS

class LinearActuator:
    def __init__(self, pinLA , pinEnable):
        self.pinLA = pinLA
        self.pinEnable = pinEnable
        GPIO.setup(self.pinLA, GPIO.OUT)
        GPIO.setup(self.pinEnable, GPIO.OUT)
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm = GPIO.PWM(pinLA, 50)
        self.pwm.start(7)
        time.sleep(0.5)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'default'

    def extend(self):
        print('Extending linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(8.2)
        time.sleep(0.5)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'extended'

    def retract(self):
        print('Retracting linear actuator.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(5.6)
        time.sleep(0.5)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'retracted'

    def default(self):
        print('Moving linear actuator to default(center) position.')
        GPIO.output(self.pinEnable, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(7)
        time.sleep(0.5)
        GPIO.output(self.pinEnable, GPIO.LOW)
        self.state = 'default'

class Valve:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False

    def switch(self):
        if self.state == False:
            self.enable()
        elif self.state == True:
            self.disable()

    def enable(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = True
        print(self.name + ' enabled.')

    def disable(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        print(self.name + ' disabled.')

class MOS:
    def __init__(self, adc, channel):

        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144

    def read(self):
        self.conversion_value = (self.adc.read_adc(self.channel,gain=self.GAIN)/pow(2, 15))*6.144
        return self.conversion_value

    def print(self):
        self.read()
        print("\nReading from MOS: {}".format(self.conversion_value))

class TemperatureSensor():
    def __init__(self, adc, channel):

        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = self.adc.read_adc(self.channel,gain=self.GAIN)

    def read(self):
        self.conversion_value = self.adc.read_adc(self.channel,gain=self.GAIN)
        return self.conversion_value

    def print(self):
        self.read()
        print("\nReading from Temperature Sensor: {}".format(self.conversion_value))

class all_sensors:
    def __init__(self,sens1,sens2,sens3,sens4):
        self.sens1 = sens1
        self.sens2 = sens2
        self.sens3 = sens3
        self.sens4 = sens4
        self.sensVal1 = self.sens1.read()
        self.sensVal2 = self.sens2.read()
        self.sensVal3 = self.sens3.read()
        self.sensVal4 = self.sens4.read()
    def read(self):
        self.sensVal1 = self.sens1.read()
        self.sensVal2 = self.sens2.read()
        self.sensVal3 = self.sens3.read()
        self.sensVal4 = self.sens4.read()
        return self.sensVal1, self.sensVal2, self.sensVal3, self.sensVal4

    def print(self):
        temp1,temp2,temp3,temp4 = self.read()
        print("\nReading from all Sensors: \n{}".format(self.read()))

class PressureSensor():
    def __init__(self, adc, channel):

        self.GAIN = 2 / 3
        self.adc = adc
        self.channel = channel
        self.conversion_value = self.adc.read_adc(self.channel,gain=self.GAIN)

    def read(self):
        self.conversion_value = self.adc.read_adc(self.channel,gain=self.GAIN)
        return self.conversion_value

    def print(self):
        self.read()
        print("\nReading from Pressure Sensor: \n{}".format(self.conversion_value))

class Pump:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False

    def switch(self):
        if self.state == False:
            self.enable()
        elif self.state == True:
            self.disable()

    def enable(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = True
        print('Pump enabled.')

    def disable(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        print('Pump disabled.')
