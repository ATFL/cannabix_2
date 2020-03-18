import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings(False)

Sample_Pump=29
Sample_Pump_Retract=31
Waste_Pump=33
Water_Pump=36
P_Valve=37
button = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Sample_Pump, GPIO.OUT)
GPIO.setup(Sample_Pump_Retract, GPIO.OUT)
GPIO.setup(Water_Pump, GPIO.OUT)
GPIO.setup(Waste_Pump, GPIO.OUT)
GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def readButton():
    return GPIO.input(button)

while(True):
    buttonStat = readButton()
    if(buttonStat == GPIO.HIGH):
        print("Saplme Delivery")
        GPIO.output(Sample_Pump, GPIO.HIGH)
        GPIO.output(Sample_Pump_Retract, GPIO.LOW)
        sleep(5)
        GPIO.output(Sample_Pump, GPIO.LOW)

        # Waste pump enabled
        # Sample pump retract
        print("Extraction")
        GPIO.output(Sample_Pump_Retract, GPIO.HIGH)
        GPIO.output(Waste_Pump, GPIO.HIGH)
        sleep(5)
        GPIO.output(Sample_Pump_Retract, GPIO.LOW)
        GPIO.output(Waste_Pump, GPIO.LOW)

        # Water pump deliver
        print("Water Delivery")
        GPIO.output(Water_Pump, GPIO.HIGH)
        sleep(5)
        GPIO.output(Water_Pump, GPIO.LOW)

        # waste pump enabled
        print("Extraction")
        GPIO.output(Waste_Pump, GPIO.HIGH)
        sleep(5)
        GPIO.output(Waste_Pump, GPIO.LOW)

        print("Test Cycle Complete")

GPIO.cleanup()
