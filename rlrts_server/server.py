import re

from rlrts_server import world
from itertools import repeat

from zmq.core import context, socket
from zmq.eventloop import zmqstream

teams = {"Herp": ["James", "Ben", "Smelly"],
         "Derp": ["Kit", "George", "Rose"]
        }

teams_connected = ["Herp", "Derp"]

devices = [(1, (26, 25)),
           (2, (27, 25)),
           (3, (28, 25)),
           (4, (29, 25)),
           (5, (30, 25)),
           (6, (31, 25))]


class Server(object):
    position_re = re.compile("\(([^,]+), ?\(([0-9]+(?:\.[0-9]+)?), ?([0-9]+(?:\.[0-9]+)?), ?([0-9]+(?:\.[0-9]+)?)\)\)")

    def __init__(self):
        self.state = "Initialization"
        self.ctx = context.Context(3)
        self.socket = self.ctx.socket(socket.ROUTER)
        self.socket.bind("tcp://*:31415")
        self.stream = zmqstream.ZMQStream(self.socket)
        self.stream.on_recv(self.recv)
        self.seen = {}
        self.current_orders = {}
        self.units = {}

        # Use the data entered on the web interface to prepopulate things
        ## Populate teams from known set
        self.teams = {}
        for team in teams_connected:
            self.setup_team(team)

        ## Prepare unit names from known set
        self.remaining_names = []
        for key in teams:
            self.remaining_names.extend(zip(teams[key], repeat(key)))

    def setup_world(self, (w, h), (bx, by, bz)):
        self.world = world.World((w, h), (bx, by, bz))
        for key in self.teams:
            self.teams[key].set_world(self.world)

    def assign_unit(self, device_id, (x, y)):
        (name, team_name) = self.remaining_names.pop()
        unit = world.Unit(device_id, name, (x, y))
        self.teams[team_name].add_unit(unit)
        self.units[device_id] = unit
        return (device_id, name)

    def setup_team(self, team_name):
        self.teams[team_name] = world.Team(team_name)

    def send(self, recipient, msg):
        out = [recipient, ""] + msg
        print "Sending: %s" % (out,)
        self.stream.send_multipart(out)

    def recv(self, msg):
        sender = msg[0]
        msg_type = msg[2]
        payload = msg[3:]
        if sender in self.seen:
            self.dispatch(sender, msg_type, payload)
        else:
            self.initialize(sender, msg_type, payload)

    def initialize(self, sender, msg_type, payload):
        print payload
        if msg_type.startswith("PI"):
            # Initialize the raspberry pi connection
            ## First two entries are width, height
            width, height = map(int, payload[:2])
            ## The next three are the location of the base station
            bx, by, bz = map(float, payload[2:5])
            self.setup_world((width, height), (bx, by, bz))

            # The rest of the entries will be device ids
            device_ids = payload[5:]
            names = []
            for device_id in device_ids:
                # We assume the devices are currently at the base station
                names.append(self.assign_unit(device_id, (bx, by)))
            self.send(sender, map(str, names))
            self.seen[sender] = True
        elif msg_type.startswith("CLIENT"):
            # The payload will be [the team name]
            self.seen[sender] = self.teams[payload[0]]
            self.send(sender, payload)
        else:
            print "Sending back"
            self.send(sender, ["received"])

    def dispatch(self, sender, msg_type, payload):
        if msg_type.startswith("PI"):
            if msg_type.startswith("PI_REQ"):
                # The pi is requesting orders
                self.send(sender, self.current_orders.items())
            elif msg_type.startswith("PI_PUSH"):
                # The pi is sending positions
                for pos in payload:
                    # Extract the device id and position using regex
                    m = self.position_re.match(pos)
                    device_id = m.group(1)
                    x, y, z = map(lambda n: float(m.group(n)), [2, 3, 4])
                    self.units[device_id].move((x, y))
                    self.send(sender, ["received"])
        elif msg_type.startswith("CLIENT"):
            if msg_type.startswith("CLIENT_REQ"):
                # The client is requesting positions
                pass
            elif msg_type.startswith("CLIENT_PUSH"):
                # The client is sending orders
                pass

if __name__ == "__main__":
    s = Server()
    s.stream.io_loop.start()
