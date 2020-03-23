import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT)

pwm = GPIO.PWM(16,50)
pwm.start(6)
x = 5
while x != 0:
	x = float(input("what val: "))
	pwm.ChangeDutyCycle(x)

pwm.stop()
GPIO.cleanup()

