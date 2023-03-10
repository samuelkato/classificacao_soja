#!/usr/bin/env python3
# codigo que deve controlar os 2 servos de cada impressora
# versao 1.0.1

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
#ads.gain = 16;
ads.gain = 1;
ads.mode = 0

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P1)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format('raw', 'v'))
interval = 0.005
a = [];
nAmostras = 100
while True:
	v = chan.value;
	a.append(v)
	if len(a) >= nAmostras:
		#a = a[-nAmostras:]
		soma = 0;
		for val in a:
			soma += val
		umidade = 14.2 + (soma/nAmostras - 19870) * -0.003784
		print("{:.2f}\t{:>5}\t{}".format(umidade,soma/nAmostras,a[0:5]+['...']))
		a = []
		#print(len(a))
	
	
	#print("{:>5}".format(soma/nAmostras))
	
	time.sleep(interval)
