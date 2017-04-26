from flask import Flask, render_template, Response
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from camera_pi import Camera


import RPi.GPIO as GPIO
import time
import atexit

GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER=18
GPIO_ECHO =24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

app = Flask(__name__)
mh = Adafruit_MotorHAT(addr=0x60)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)


myMotor1 = mh.getMotor(1)
myMotor4 = mh.getMotor(4)
myMotor1.setSpeed(200)
myMotor4.setSpeed(200)


@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
					
@app.route("/<direction>")
def move(direction):
        dist = distance()
        
	if direction =='forward' and dist>5:
		myMotor1.run(Adafruit_MotorHAT.FORWARD)
                myMotor4.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(0.5)
		myMotor1.run(Adafruit_MotorHAT.RELEASE)
                myMotor4.run(Adafruit_MotorHAT.RELEASE)
                time.sleep(0.1)
		
		
	elif direction =='reverse':
		myMotor1.run(Adafruit_MotorHAT.BACKWARD)
                myMotor4.run(Adafruit_MotorHAT.BACKWARD)
		time.sleep(0.5)
		myMotor1.run(Adafruit_MotorHAT.RELEASE)
                myMotor4.run(Adafruit_MotorHAT.RELEASE)
                time.sleep(0.1)

	elif direction =='right' and dist>5:
		myMotor1.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(0.5)
		myMotor1.run(Adafruit_MotorHAT.RELEASE)
                time.sleep(0.1)

	elif direction =='left' and dist>5:
		myMotor4.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(0.5)
		myMotor4.run(Adafruit_MotorHAT.RELEASE)
                time.sleep(0.1)

		
	return direction
	
if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True, threaded=True)
