#!/usr/bin/env python3
# codigo que deve controlar os 2 servos de cada impressora
# versao 1.0.1

#import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import requests
import time
import threading
#import cv2 #super pesado
#import numpy as np #super pesado
#import subprocess
import pigpio
import signal
import RPi.GPIO as GPIO
import sys
import math
import argparse
import os, os.path
import imutils
import pigpio
from datetime import datetime
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn



"""
#controle da chave que libera o conteudo para o avaliador

while 1:
		if input("y/n: ")=="y":
			pi.set_servo_pulsewidth(4, 500)
		else:
			pi.set_servo_pulsewidth(4, 2000)"""

class rpiPrinter:
	camera = None;
	parar_ = False;
	servoPin = 4;
	luzPin = 17;
	btnPin = 18;
	resx = 1024
	resy = 1024
	fps = 10
	chan = None;
	imgNo = 1
	exibirFrames = False #precisa de display
	image = None
	aEnvios = [];
	imgsDir = os.path.dirname(os.path.abspath(__file__))+'/imgs';
	nextID = None;
	clienteID = None;
	pig = None;
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.luzPin, GPIO.OUT)
		GPIO.setup(self.btnPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		GPIO.output(self.luzPin, GPIO.LOW)
		self.pig = pigpio.pi()
		
		fileID = os.path.dirname(os.path.abspath(__file__))+'/clienteID.txt'
		if os.path.isfile(fileID):
			self.clienteID = open(fileID,'r').read().strip();
		print("clienteID:"+self.clienteID)
		# Create the I2C bus
		try:
			i2c = busio.I2C(board.SCL, board.SDA)
			# Create the ADC object using the I2C bus
			ads = ADS.ADS1015(i2c)

			# Create single-ended input on channel 0
			#self.chan = AnalogIn(ads, ADS.P0)

			# Create differential input between channel 0 and 1
			self.chan = AnalogIn(ads, ADS.P0, ADS.P1)
		except Exception as err:
			print("erro ao conectar com o sensor de umidade");
			class Sensor(object):
				value = 'error'
				def __init__(self):
					pass
			self.chan = Sensor()
			

		
		if not os.path.isdir(self.imgsDir):
			os.mkdir(self.imgsDir);
		self.nextID = (sorted([int(name.split('.')[0]) for name in os.listdir(self.imgsDir) if os.path.isfile(self.imgsDir+"/"+name) and name.split('.')[0].isdigit()]) or [0])[-1] + 1;
		
		#len([name for name in os.listdir(pasta) if os.path.isfile(pasta+"/"+name)])+1
		
		# initialize the camera and grab a reference to the raw camera capture
		self.camera = PiCamera()
		self.camera.awb_mode='off'
		self.camera.awb_gains=(1.8, 1.3)
		#self.camera.exposure_mode='off'#backlight setar como off apos um tempo
		#self.camera.digital_gain = 0
		self.camera.shutter_speed=10000
		self.camera.brightness = 50
		self.camera.ISO = 100
		self.camera.meter_mode = 'spot'
		self.camera.contrast=0
		self.camera.drc_strength= 'off'
		self.camera.resolution = (self.resx, self.resy)
		self.camera.framerate = self.fps
		#rawCapture = PiRGBArray(self.camera, size=(self.resx, self.resy))
		 
		# allow the camera to warmup
		#time.sleep(0.1)
		
		threading.Thread(target = self.threadTeclado).start();
		threading.Thread(target = self.threadNetwork).start();
		
		# capture frames from the camera
		#for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		#	if self.parar_:
		#		break;
		#	#threading.Thread(target = self.procImage, args=[frame.array]).start();
		#	self.image = frame.array
		#	rawCapture.truncate(0)
		
		def handler(signum, frame):
			GPIO.cleanup()
			self.parar_ = True;

		signal.signal(signal.SIGINT, handler)
	
	def threadTeclado(self):
		while not self.parar_:
			#esse input deve vir de um GPIO
			#if input("y/n: ")=="y":
			if GPIO.input(self.btnPin) == 0: #input("y/n: ")=="y":
				#travar servo
				self.pig.set_servo_pulsewidth(self.servoPin, 500)
				while GPIO.input(self.btnPin) == 0:
					time.sleep(0.1)
				#adicionar input de btn que deve ser substituido por alguma outra coisa
				print("apertou botao")
				#imgExib = self.image;#imutils.resize(self.image, width=400)
				fileName = self.imgsDir+"/"+(("00000"+str(self.nextID))[-6:])+".png"
				#cv2.imwrite(fileName, self.image)
				
				GPIO.output(self.luzPin, GPIO.HIGH)
				self.camera.capture(fileName)
				GPIO.output(self.luzPin, GPIO.LOW)
				total = 100;
				v = 0;
				for _ in range(total):
					v += self.chan.value;
					time.sleep(0.01)
				umidade = 14.2 + (v/total - 20635) * -0.00403
				self.aEnvios.append({
					'clienteID':self.clienteID,
					'img':fileName,
					"umidade" : str(umidade)+" ("+str(self.chan.value)+")",
					'data' : datetime.today().strftime('%Y-%m-%d %H:%M:%S')
					#tentar conseguir placa ou tag da carreta
				});
				self.nextID += 1;
				#cv2.imshow("image", imgExib);
				#cv2.waitKey(1);
				
				
				self.pig.set_servo_pulsewidth(self.servoPin, 2000)
				#liberar servo
			else:
				#self.parar_ = True;
				time.sleep(0.1)
	
	def threadNetwork(self):
		while not self.parar_:
			if len(self.aEnvios)>0:
				try:
					oEnvio = self.aEnvios[0]
					r = requests.post("http://samuelkato.ddns.net:3000/upload",timeout=5, files={'file': open(oEnvio['img'],'rb')},data={"clienteID":oEnvio['clienteID'],"umidade":oEnvio['umidade'],"data":oEnvio['data']})
					if(r.text != 'True'):
						raise ValueError;
					#os.remove(oEnvio['img'])
					self.aEnvios = self.aEnvios[1:]
					print("enviou com sucesso");
				except requests.exceptions.RequestException as e:
					print("ops, deu erro")
					time.sleep(5);
				except ValueError:
					print("ops, deu erro")
					time.sleep(5);
			time.sleep(0.1);
	
p = rpiPrinter()

