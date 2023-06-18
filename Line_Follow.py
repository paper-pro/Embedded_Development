#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from neopixel import Adafruit_NeoPixel, Color
from TRSensors import TRSensor
import time

Button = 7

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Button,GPIO.IN,GPIO.PUD_UP)

# LED strip configuration:
LED_COUNT      = 4      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)	

maximum = 15
j = 0
integral = 0
last_proportional = 0

def Wheel(pos):
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()
strip.setPixelColor(0, Color(100, 0, 0))       #Red
strip.setPixelColor(1, Color(0, 100, 0))       #Blue
strip.setPixelColor(2, Color(0, 0, 100))       #Green
strip.setPixelColor(3, Color(100, 100, 0))     #Yellow
strip.show()

TR = TRSensor()
Ab = AlphaBot2()
Ab.stop()
print("Line follow Example")
time.sleep(0.5)
for i in range(0,100):
	if(i<25 or i>= 75):
		Ab.right()
		Ab.setPWMA(15)
		Ab.setPWMB(15)
	else:
		Ab.left()
		Ab.setPWMA(15)
		Ab.setPWMB(15)
	TR.calibrate()
Ab.stop()
print(TR.calibratedMin)
print(TR.calibratedMax)
while (GPIO.input(Button) != 0):
	position,Sensors = TR.readLine()
	print(position,Sensors)
	time.sleep(0.05)
Ab.forward()

while True:
	try:
		position,Sensors = TR.readLine()
		if(Sensors[0] >900 and Sensors[1] >900 and Sensors[2] >900 and Sensors[3] >900 and Sensors[4] >900):
			Ab.setPWMA(0)
			Ab.setPWMB(0)
		else:
			proportional = position - 2000
			derivative = proportional - last_proportional
			integral += proportional
			last_proportional = proportional
			power_difference = proportional/30  + integral/10000 + derivative*2;  
			if (power_difference > maximum):
				power_difference = maximum
			if (power_difference < - maximum):
				power_difference = - maximum
			print(position,power_difference)
			if (power_difference < 0):
				Ab.setPWMA(0)
				Ab.setPWMB(-power_difference)
			else:
				Ab.setPWMA(power_difference)
				Ab.setPWMB(0)
		for i in range(0,strip.numPixels()):
			strip.setPixelColor(i, Wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		j += 1
		if(j > 256*4): 
			j= 0
	except KeyboardInterrupt:
		break
