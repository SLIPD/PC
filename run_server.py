#!/usr/bin/env python
from rlrts_server import server


s = server.Server()
print "Starting"
s.ioloop.add_callback(server.print_ready)
try:
    s.ioloop.start()
except KeyboardInterrupt:
    print "Finished"
