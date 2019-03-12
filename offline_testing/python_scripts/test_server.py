from multiprocessing.connection import Listener
import numpy

address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
listener = Listener(address, authkey=b'secret password')
#conn = listener.accept()
#print( 'connection accepted from', listener.last_accepted)
#while True:

while(1):
	with listener.accept() as conn:
		print('connection accepted from', listener.last_accepted)
		timeString = conn.recv()
		respRate = conn.recv()
		rateMag = conn.recv()
		phasePoints = conn.recv()
		print(timeString)
		print(respRate)
		print(rateMag)
		print(phasePoints)

		#convert to numpy array if needed 
		phasePointInput = numpy.array(phasePoints)
		print(type(phasePointInput))
		#msg = conn.recv()
		#print(msg)
		#if msg == 'close':
		#	conn.close()
		#	break

listener.close()