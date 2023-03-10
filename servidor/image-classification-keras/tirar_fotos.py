#!/usr/bin/env python3
# codigo que deve controlar os 2 servos de cada impressora
# versao 1.0.1

#import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading
import cv2 #super pesado
import numpy as np #super pesado
import subprocess
import pigpio
import RPi.GPIO as GPIO
import sys
import math
import argparse
import os, os.path
import imutils

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True,
	help="output directory")
pasta = vars(ap.parse_args())['directory']

class rpiPrinter:
	parar_ = False;
	
	resx = 1024
	resy = 1024
	fps = 10
	imgNo = 1
	exibirFrames = False #precisa de display
	image = None
	
	def __init__(self):
		if not os.path.isdir(pasta):
			os.makedirs(pasta)
		self.imgNo = len([name for name in os.listdir(pasta) if os.path.isfile(pasta+"/"+name)])+1
		
		
		# initialize the camera and grab a reference to the raw camera capture
		camera = PiCamera()
		camera.awb_mode='off'
		camera.awb_gains=(1.8, 1.0)
		camera.exposure_mode='off'#backlight setar como off apos um tempo
		#camera.digital_gain = 0
		camera.shutter_speed=1000
		camera.brightness = 50
		camera.ISO = 100
		camera.meter_mode = 'spot'
		camera.contrast= 0
		camera.drc_strength= 'off'
		camera.resolution = (self.resx, self.resy)
		camera.framerate = self.fps
		rawCapture = PiRGBArray(camera, size=(self.resx, self.resy))
		 
		# allow the camera to warmup
		time.sleep(0.1)
		
		#threading.Thread(target = self.threadAcao).start();
		#threading.Thread(target = self.threadBtns).start();
		threading.Thread(target = self.threadTeclado).start();
		
		# capture frames from the camera
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			#threading.Thread(target = self.procImage, args=[frame.array]).start();
			self.image = frame.array
			imgExib = imutils.resize(self.image, width=400)
			cv2.imshow("image", imgExib);
			cv2.waitKey(1);
			rawCapture.truncate(0)
	
	def threadTeclado(self):
		ladoQuad = 200
		while True:
			strNo = ("0000000"+str(self.imgNo))[-8:];
			input("aperte enter para salvar a imagem "+strNo)
			w, h, ch = self.image.shape
			wAt = ladoQuad;
			while wAt < w:
				hAt = ladoQuad;
				while hAt < h:
					strNo = ("0000000"+str(self.imgNo))[-8:];
					cv2.imwrite(pasta+"/"+strNo+".png",self.image[hAt-ladoQuad:hAt, wAt-ladoQuad:wAt])
					self.imgNo+=1
					hAt += ladoQuad
				wAt += ladoQuad
	
p = rpiPrinter()

