import re

from rlrts_server import world
from itertools import repeat

from zmq.core import context, socket
from zmq.eventloop import zmqstream, ioloop
from zmq.utils import jsonapi

teams = {"Herp": ["James", "Ben", "Smelly"],
         "Derp": ["Kit", "George", "Rose"]
        }
n_players = 0

zero = (55.943721, -3.175135)
tr = (55.953573, -3.155394)
for l in teams.values():
    n_players += len(l)

teams_connected = ["Herp", "Derp"]


class Server(object):
    def __init__(self, render=None):
        # Make a context
        self.ctx = context.Context(3)
        self.ioloop = ioloop.IOLoop.instance()

        # Make the PI socket
        self.pi_socket = self.ctx.socket(socket.PAIR)
        self.pi_port = self.pi_socket.bind_to_random_port("tcp://*")

        self.pi_stream = zmqstream.ZMQStream(self.pi_socket,
                                             self.ioloop)
        self.pi_stream.on_recv(self.recv_pi)

        # Prepare for team sockets
        self.team_sockets = {}

        # Make the main router socket
        self.socket = self.ctx.socket(socket.ROUTER)
        self.socket.bind("tcp://*:31415")

        self.stream = zmqstream.ZMQStream(self.socket,
                                          self.ioloop)
        self.stream.on_recv(self.recv)

        self.seen = {}
        self.current_orders = {}
        self.units = {}

        self.render = render

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
        sock = self.ctx.socket(socket.PAIR)
        p = sock.bind_to_random_port("tcp://*")

        stream = zmqstream.ZMQStream(sock, self.ioloop)
        stream.on_recv(self.recv_client(team_name))

        self.team_sockets[team_name] = (p, stream, sock)

    def send(self, recipient, msg):
        out = [recipient, ""] + msg
        print "Sending: %s" % (out,)
        self.stream.send_multipart(out)

    def recv(self, msg):
        sender = msg[0]
        msg_type = msg[2]
        payload = msg[3:]
        self.initialize(sender, msg_type, payload)

    def initialize(self, sender, msg_type, payload):
        if msg_type.startswith("PI"):
            # Initialize the raspberry pi connection
            self.send(sender, [self.pi_port, n_players, zero[0], zero[1]])
        elif msg_type.startswith("CLIENT"):
            # The payload will be [the team name]
            self.send(sender, [str(self.team_sockets[payload[0]][0])])

    def recv_pi(self, message):
        print "Receive PI"
        try:
            j = jsonapi.loads(''.join(message))
            m = "JSON: " + str(j)

            if j['state'] == 'init':
                # Perform initialisation steps
                (width, height) = map(int, j['dimensions'])
                print "dims: (%d, %d)" % (width, height)
                (bx, by, bz) = j['base_location']
                print "base: (%d, %d, %d)" % (bx, by, bz)
                self.setup_world((width, height), (bx, by, bz))

                names = []
                for device_id in j['device_ids']:
                    names.append(self.assign_unit(device_id, (bx, by)))
                    print "Device \"%s\" is called %s" % names[-1]

                r = {"state": "naming",
                     "mapping": dict(names)
                    }

                print "Sending %s" % r

                self.pi_stream.send_json(r)

                if self.render is not None:
                    self.render.ready()
            elif j['state'] == 'play':
                for (device_id, (x, y, z)) in j['updates']:
                    print "%s has moved to (%d, %d, %d)" % (device_id, x, y, z)
                    self.units[device_id].move((x, y))
                if self.render is not None:
                    self.render.step()
        except jsonapi.jsonmod.JSONDecodeError:
            m = "String: " + ''.join(message)
        print m

    def recv_client(self, team_name):
        team = self.teams[team_name]

        def inner_function(message):
            print "Receive team: %s" % team_name
            try:
                m = "JSON: " + str(jsonapi.loads(''.join(message)))
            except jsonapi.jsonmod.JSONDecodeError:
                m = "String: " + ''.join(message)
            print m

        return inner_function

    def dispatch(self, sender, msg_type, payload):
        if msg_type.startswith("PI"):
            pass
        elif msg_type.startswith("CLIENT"):
            if msg_type.startswith("CLIENT_REQ"):
                # The client is requesting positions
                pass
            elif msg_type.startswith("CLIENT_PUSH"):
                # The client is sending orders
                pass

if __name__ == "__main__":
    s = Server()
    print "Starting"
    s.ioloop.start()
