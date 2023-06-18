#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time

CS = 5
Clock = 25
Address = 24
DataOut = 23
Button = 7

class TRSensor(object):
	def __init__(self,numSensors = 5):
		self.numSensors = numSensors
		self.calibratedMin = [0] * self.numSensors
		self.calibratedMax = [1023] * self.numSensors
		self.last_value = 0
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(Clock,GPIO.OUT)
		GPIO.setup(Address,GPIO.OUT)
		GPIO.setup(CS,GPIO.OUT)
		GPIO.setup(DataOut,GPIO.IN,GPIO.PUD_UP)
		GPIO.setup(Button,GPIO.IN,GPIO.PUD_UP)

	def AnalogRead(self):
		value = [0]*(self.numSensors+1)
		for j in range(0,self.numSensors+1):
			GPIO.output(CS, GPIO.LOW)
			for i in range(0,10):
				if i<4:
					bit = ((j) >> (3 - i)) & 0x01
					GPIO.output(Address,bit)
				value[j] <<= 1
				value[j] |= GPIO.input(DataOut)
				GPIO.output(Clock,GPIO.HIGH)
				GPIO.output(Clock,GPIO.LOW)
			GPIO.output(CS,GPIO.HIGH)
			time.sleep(0.0001)
		return value[1:]
		
	def calibrate(self):
		max_sensor_values = [0]*self.numSensors
		min_sensor_values = [0]*self.numSensors
		for j in range(0,10):		
			sensor_values = self.AnalogRead()			
			for i in range(0,self.numSensors):
				if((j == 0) or max_sensor_values[i] < sensor_values[i]):
					max_sensor_values[i] = sensor_values[i]
				if((j == 0) or min_sensor_values[i] > sensor_values[i]):
					min_sensor_values[i] = sensor_values[i]
		for i in range(0,self.numSensors):
			if(min_sensor_values[i] > self.calibratedMin[i]):
				self.calibratedMin[i] = min_sensor_values[i]
			if(max_sensor_values[i] < self.calibratedMax[i]):
				self.calibratedMax[i] = max_sensor_values[i]

	def	readCalibrated(self):
		value = 0
		sensor_values = self.AnalogRead()
		for i in range (0,self.numSensors):
			denominator = self.calibratedMax[i] - self.calibratedMin[i]
			if(denominator != 0):
				value = (sensor_values[i] - self.calibratedMin[i])* 1000 / denominator				
			if(value < 0):
				value = 0
			elif(value > 1000):
				value = 1000				
			sensor_values[i] = value
		return sensor_values
			
	def readLine(self, white_line = 0):
		sensor_values = self.readCalibrated()
		avg = 0
		sum = 0
		on_line = 0
		for i in range(0,self.numSensors):
			value = sensor_values[i]
			if(white_line):
				value = 1000-value
			if(value > 200):
				on_line = 1
			if(value > 50):
				avg += value * (i * 1000); 
				sum += value; 

		if(on_line != 1):
			if(self.last_value < (self.numSensors - 1)*1000/2):
				self.last_value = 0
			else:
				self.last_value = (self.numSensors - 1)*1000
		else:
			self.last_value = avg/sum
		return self.last_value,sensor_values
	

if __name__ == '__main__':
	TR = TRSensor()
	print("TRSensor Example")
	while True:
		try:
			print(TR.AnalogRead())
			time.sleep(0.2)
		except KeyboardInterrupt:
			break
			 
