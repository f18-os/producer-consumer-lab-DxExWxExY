#!/usr/bin/env python3

import threading, cv2, numpy, base64, os, time, sys
from queue import Queue

cq = Queue(10)
dq = Queue(10)

c = threading.Condition()
d = threading.Condition()

class Extract(threading.Thread):
	"""Extracts Frames"""
	def run(self):
		global cq, c
		count = 0
		vidcap = cv2.VideoCapture('clip.mp4')
		# read one frame
		success,image = vidcap.read()
		cq.put(image)
		print("Reading frame {} {} ".format(count, success))
		while success:
			c.acquire()
			if cq.full():
				c.wait()
		 	# write the current frame to the queue
			success,image = vidcap.read()
			count += 1
			cq.put(image)
			# notify conditions
			c.notify()
			c.release()
			time.sleep(0.001)
		print("Killing Extract")
		sys.exit(0)
# End Extract

class Convert(threading.Thread):
	"""Converts Frames"""
	def run(self):
		global cq, dq, c, d
		count = 0 
		# get the next frame
		inputFrame = cq.get()
		while inputFrame is not None:
			c.acquire()
			d.acquire()
			if cq.empty():
				c.wait()
			if dq.full():
				d.wait()
			print("Converting frame {}".format(count))
			# convert the image to grayscale
			grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
			dq.put(grayscaleFrame)
			count += 1
			# generate input file name for the next frame
			inFileName = "{}/frame_{:04d}.jpg".format('frames', count)
			# load the next frame
			inputFrame = cq.get()
			# notify conditions
			c.notify()
			c.release()
			d.notify()
			d.release()
			time.sleep(0.001)
		print("Killing Convert")
		d.acquire()
		dq.put(None)
		d.notify()
		d.release()
		sys.exit(0)
# End Convert
class Display(threading.Thread):
	"""Displays Frames"""
	def run(self):
		global dq, d
		count = 0
		startTime = time.time()
		# load the frame
		frame = dq.get()
		while frame is not None:
			d.acquire()
			if dq.empty():
				d.wait()
			print("Displaying frame {}".format(count))
			# Display the frame in a window called "Video"
			cv2.imshow("Video", frame)
			# compute the amount of time that has elapsed
			# while the frame was processed
			elapsedTime = int((time.time() - startTime) * 1000)
			print("Time to process frame {} ms".format(elapsedTime))
			# determine the amount of time to wait, also
			# make sure we don't go into negative time
			timeToWait = max(1, 42 - elapsedTime)
			# Wait for 42 ms and check if the user wants to quit
			if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
				print("Killing Display")
				cv2.destroyAllWindows()
				break    
			# get the start time for processing the next frame
			startTime = time.time()
			# get the next frame filename
			count += 1
			# Read the next frame file
			frame = dq.get()
			# notify conditions
			d.notify()
			d.release()
			time.sleep(0.001)
		print("Killing Display")
		cv2.destroyAllWindows()
		sys.exit(0)
		
if __name__ == '__main__':
	Extract().start()
	Convert().start()
	Display().start()