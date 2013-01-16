import socket
import sys
import zmq
import pdb

from zmq.eventloop.zmqstream import ZMQStream

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setblocking(0);
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)


# ZMQ STUFF
ctx = zmq.Context()
command_socket = ctx.socket(zmq.REQ)
command_socket.connect("tcp://176.31.243.99:40000" )#"tcp://{0}:{1}".format(sys.argv[1], sys.argv[2])) "tcp://176.31.243.99:40000"
command_stream = ZMQStream(command_socket)
pair_socket = None
pair_stream = None

def send():
	pair_stream.io_loop.add_callback(send)
	b = ''
	data = ""
	try:
		#print >>sys.stderr, "Still doing stuff"
		while(b!='\0'):
			#print b
			b = connection.recv(1)
			if(b!='\0'):
				data += b
			#if data != "":
		print >>sys.stderr, 'received "%s"' % data
		pair_stream.send(data)	#(data)
		pair_stream.flush()
	except:
		pass


def recv(msg):
    	global pair_socket, pair_stream
    	print msg
    	port = int(msg[0])
    	print port
    	pair_socket = ctx.socket(zmq.PAIR)
    	pair_socket.connect("tcp://176.31.243.99:%d" % port)
    	pair_stream = ZMQStream(pair_socket, command_stream.io_loop)
    	pair_stream.on_recv(pair_recv)
    	send()

def pair_recv(msg):
	print "Message: " + ''.join(msg)
	connection.sendall(''.join(msg))

while True:
    	# Wait for a connection
	print >>sys.stderr, 'waiting for a connection'
	sock.setblocking(0)
	sock.settimeout(0.0)
	done = False
	while not done:
		try:
			connection, client_address = sock.accept()
			done = True
		except socket.error:
			pass
	print "Not Blocking"
	command_stream.on_recv(recv)
	team = raw_input("Team name: ")
	command_stream.send_multipart(["CLIENT", team])
	command_stream.io_loop.start()