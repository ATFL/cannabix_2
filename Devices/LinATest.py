import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
#GPIO.setup(22,GPIO.OUT)
GPIO.setup(38,GPIO.OUT)

#GPIO.output(16,GPIO.HIGH)
pwm = GPIO.PWM(38,50)
pwmVal = 7
pwm.start(pwmVal)

while(pwmVal != 0):
    pwmVal = float(input("What PWM: "))
    pwm.ChangeDutyCycle(pwmVal)
    time.sleep(1.5)

pwm.stop()
GPIO.cleanup()
