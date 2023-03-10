# USAGE
# python test_network.py --model santa_not_santa.model --image images/examples/santa_01.png

# import the necessary packages
print("[INFO] carregando modulos")
import RPi.GPIO as GPIO
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import imutils
import cv2
import sys
import threading
from picamera.array import PiRGBArray
from picamera import PiCamera
from fractions import Fraction
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to trained model model")
args = vars(ap.parse_args())
print("[INFO] loading network...")
model = load_model(args["model"])

dout = 24
pd_sck = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(pd_sck, GPIO.OUT)
GPIO.setup(dout, GPIO.IN)

oLabels = {
	0:'ab',
	1:'aj',
	2:'fe',
	3:'f2',
	4:'v',
	5:'mi',
	6:'q',
	7:'so',
	8:'v2',
}

lSize = 20
ladoQuad = 200

resx = 1024
resy = 1024
fps = 5

def analisaImg(orig):
	w, h, ch = orig.shape
	wAt = ladoQuad;
	
	aAvg = [];
	for key in oLabels:
		aAvg.append(0)
	n = 0
	while wAt < w:
		hAt = ladoQuad;
		while hAt < h:
			image = orig[hAt-ladoQuad:hAt, wAt-ladoQuad:wAt]
			image = cv2.resize(image, (lSize, lSize))
			
			image = image.astype("float") / 255.0
			image = img_to_array(image)
			image = np.expand_dims(image, axis=0)

			res = model.predict(image)[0];
			for i in range(0,len(res)):
				aAvg[i] += res[i];
			n+=1
			hAt += ladoQuad
		wAt += ladoQuad
	
	
	label = '';	
	for i in range(0,len(aAvg)):
		label += ("{}: {:.0f}".format(str(i), aAvg[i] / n * 100))+" ";
	
	# build the label

	# draw the label on the image
	orig = imutils.resize(orig, width=400)
	cv2.putText(orig, label, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 128), 1)

	# show the output image
	
	cv2.putText(orig, str(getPeso())+'g', (10, 50),  cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 128, 0), 2)
	
	cv2.imshow("image", orig);
	cv2.waitKey(1);
	
def getPeso():
	while GPIO.input(dout) != 0:
		pass
	bits = []
	for i in range(24):
		GPIO.output(pd_sck, True)
		bits.append(GPIO.input(dout))
		GPIO.output(pd_sck, False)
	GPIO.output(pd_sck, True)
	GPIO.output(pd_sck, False)
	if bits[0]==False:
		print("aqui")
		return '#'
	bits[0] = 0
	bits[1] = 0
	bits[2] = 0
	bits[3] = 0
	bits[4] = 0
	bits[5] = 0
	bits[20] = 0
	bits[21] = 0
	bits[22] = 0
	bits[23] = 0
	
	ret = (int(''.join(map(str, bits)), 2) - 140846) / 257.58828596
	return round(ret * 100)/100
	
camera = PiCamera()
camera.resolution = (resx, resy)
camera.framerate = fps
camera.awb_mode='off'
camera.awb_gains=(1.8, 1.0)
camera.exposure_mode='off'
#camera.digital_gain = 0
camera.shutter_speed=1000
camera.brightness = 50
camera.ISO = 100
camera.meter_mode = 'spot'
camera.contrast= 0
camera.drc_strength= 'off'
rawCapture = PiRGBArray(camera, size=(resx, resy))
 
# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	#threading.Thread(target = self.procImage, args=[frame.array]).start();
	analisaImg(frame.array);
	#cv2.imshow("image", frame.array);
	#cv2.waitKey(1);
	rawCapture.truncate(0)

