import RPi.GPIO as GPIO
import timeVector

GPIO.setmode(GPIO.BOARD)
GPIO.setup(10,GPIO.OUT)
GPIO.setup(8,GPIO.OUT)

GPIO.output(10,GPIO.HIGH)
pwm = GPIO.PWM(8,50)
pwmVal = 7
pwm.start(pwmVal)

while(pwmVal != 0):
    pwmVal = float(input("What PWM: "))
    pwm.ChangeDutyCycle(pwmVal)
    time.sleep(0.2)

pwm.stop()
GPIO.cleanup()
