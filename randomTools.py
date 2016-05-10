import random
import math

from vec2d import vec2d

def nextCircleVector():
	angle = random.random() * 2 * math.pi
	return vec2d(math.cos(angle), math.sin(angle))
	
def nextTopQuarterVector():
	angle = random.random() * math.pi * 2 + math.pi * 5 / 4
	return vec2d(math.cos(angle), math.sin(angle))

def nextGaussian(mean, stdDev):
	x1 = 0
	x2 = 0
	y1 = 0
	z = 0

	while True:
		x1 = 2 * random.random() - 1
		x2 = 2 * random.random() - 1
		z = (x1 * x1) + (x2 * x2)

		if z < 1:
			break

	z = math.sqrt((-2 * math.log(z)) / z)
	y1 = x1 * z;
	y2 = x2 * z;

	return mean + y1 * stdDev
