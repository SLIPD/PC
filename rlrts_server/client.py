from zmq.core import context, socket
from zmq.eventloop import zmqstream
import json

ctx = context.Context.instance()
s = ctx.socket(socket.REQ)
s.connect("tcp://localhost:31415")

stream = zmqstream.ZMQStream(s)
pair_socket = None
pair_stream = None


def pair_recv(msg):
    print json.loads(''.join(msg))


def send():
    pair_stream.io_loop.add_callback(send)
    print "====================================="
    print "Message: (valid JSON or ^D to finish)"
    print "-------------------------------------"
    msg = ''
    continuing = False
    while True:
        try:
            msg += raw_input("... " if continuing else "    ")
        except EOFError:
            break
        try:
            json.loads(msg)
            break
        except ValueError:
            continuing = True
    print
    if msg == "init_pi":
        msg = """{ "state": "init",
                   "base_location": [25, 25, 0],
                   "device_ids": ["1", "2", "3", "4", "5", "6"]
                 }"""
    elif msg == "update_pi":
        msg = """{ "state": "play",
                   "updates": [["1", [20, 20, 5]], ["4", [41, 29, 9]]]
                 }"""
    elif msg == "send_commands":
        msg = """{ "Kit": [[20, 20]],
                   "Smelly": [[43, 31], [21, 42]]
                 }"""
    if msg != '':
        pair_stream.send(msg)
        pair_stream.flush()


def recv(msg):
    global pair_socket, pair_stream
    print msg
    port = int(msg[0])
    print port
    pair_socket = ctx.socket(socket.PAIR)
    pair_socket.connect("tcp://localhost:%d" % port)

    pair_stream = zmqstream.ZMQStream(pair_socket, stream.io_loop)
    pair_stream.on_recv(pair_recv)

    send()

stream.on_recv(recv)
msg_type = raw_input("msg_type: ")
if msg_type == "CLIENT":
    team = raw_input("Team name: ")
    stream.send_multipart([msg_type, team])
else:
    stream.send_multipart([msg_type])
stream.io_loop.start()
