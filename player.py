#!/usr/bin/env python3

import threading, cv2, numpy, base64, os
from queue import Queue

cq = Queue(10)
dq = Queue(10)

class Extract(threading.Thread):
	"""Extracts Frames"""
	
	def run(self):
		global cq
		count = 0
		vidcap = cv2.VideoCapture('clip.mp4')
		# create the output directory if it doesn't exist
		if not os.path.exists('frames'):
		  print("Output directory {} didn't exist, creating".format('frames'))
		  os.makedirs('frames')
		# read one frame
		success,image = vidcap.read()
		print("Reading frame {} {} ".format(count, success))
		while success and Extract.lock.acquire():
		 	# write the current frame out as a jpeg image
			cv2.imwrite("{}/frame_{:04d}.jpg".format('frames', count), image)   
			success,image = vidcap.read()
			print('Reading frame {}'.format(count))
			count += 1
			Extract.q.put(image)
			if Extract.q.full(): 
				Extract.lock.release()

# End Extract

class Convert(threading.Thread):
	"""Converts Frames"""
	def run(self):
		global cq
		# Extract.lock.acquire()
		count = 0 
		# get the next frame file name and load the next file
		inFileName = "{}/frame_{:04d}.jpg".format('frames', count)
		inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
		while inputFrame is not None and Extract.lock.acquire():
			print("Converting frame {}".format(count))
			# convert the image to grayscale
			grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
			# generate output file name
			outFileName = "{}/grayscale_{:04d}.jpg".format('frames', count)
			# write output file
			cv2.imwrite(outFileName, grayscaleFrame)
			count += 1
			# generate input file name for the next frame
			inFileName = "{}/frame_{:04d}.jpg".format('frames', count)
			# load the next frame
			inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
			if Extract.q.empty():
				Extract.lock.release()

if __name__ == '__main__':
	extract = Extract()
	extract.run()
	convert = Convert()
	convert.run()