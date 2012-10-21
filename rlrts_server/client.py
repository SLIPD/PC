from zmq.core import context, socket
from zmq.eventloop import zmqstream

ctx = context.Context.instance()
s = ctx.socket(socket.REQ)
s.connect("tcp://localhost:31415")

stream = zmqstream.ZMQStream(s)


def recv(stream, msg):
    print "What should I send?"
    msg_type = raw_input("msg_type: ")
    payload = [msg_type]
    n = 0
    done = False
    while not done:
        n += 1
        new = raw_input("payload[%d]: " % n)
        if new:
            payload.append(new)
        else:
            done = True
    stream.send_multipart(payload)

stream.on_recv_stream(recv)
stream.send("asdf")
stream.io_loop.start()
