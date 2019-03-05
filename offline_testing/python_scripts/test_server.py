from multiprocessing.connection import Listener

address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
listener = Listener(address, authkey=b'secret password')
#conn = listener.accept()
#print( 'connection accepted from', listener.last_accepted)
#while True:

while(1):
	with listener.accept() as conn:
		print('connection accepted from', listener.last_accepted)
		msg = conn.recv()
		print(msg)
		if msg == 'close':
			conn.close()
			break

listener.close()