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


def print_on_send(prefix):
    def inner_func(msg, status):
        print prefix + ''.join(msg)
    return inner_func


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
        self.pi_stream.on_send(print_on_send("Sending PI: "))

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
        self.device_ids = {}

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
        self.device_ids[name] = device_id
        return (device_id, name)

    def setup_team(self, team_name):
        self.teams[team_name] = world.Team(team_name)
        sock = self.ctx.socket(socket.PAIR)
        p = sock.bind_to_random_port("tcp://*")

        stream = zmqstream.ZMQStream(sock, self.ioloop)
        stream.on_recv(self.recv_client(team_name))
        stream.on_send(print_on_send("Sending to team \"%s\"" % team_name))

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
            self.send(sender, map(str, [self.pi_port, n_players, zero[0], zero[1]]))
        elif msg_type.startswith("CLIENT"):
            # The payload will be [the team name]
            self.send(sender, [str(self.team_sockets[payload[0]][0])])

    def recv_pi(self, message):
        print "Receive PI"
        try:
            try:
                j = jsonapi.loads(''.join(message))
            except TypeError:
                j = jsonapi.loads(message)
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

                self.pi_stream.send_json(r)

                if self.render is not None:
                    self.render.ready()
            elif j['state'] == 'play':
                for (device_id, (x, y, z)) in j['updates']:
                    print "%s has moved to (%d, %d, %d)" % (device_id, x, y, z)
                    self.units[device_id].move((x, y))
                    (i, j) = self.units[device_id].get_mesh_indices()
                    self.world.update_mesh((i, j, z))
                if self.render is not None:
                    self.render.step()
                self.send_units()
                self.send_mesh()
                self.send_steps()
        except jsonapi.jsonmod.JSONDecodeError:
            m = "String: " + ''.join(message)
        print m

    def recv_client(self, team_name):
        def inner_function(message):
            (p, stream, sock) = self.team_sockets[team_name]
            print "Receive team: %s" % team_name
            try:
                j = jsonapi.loads(''.join(message))
                m = "JSON: " + str(j)

                d = {}
                for name in j:
                    d[self.device_ids[name]] = j[name]

                r = {"state": "commanding",
                     "commands": d
                    }

                self.pi_stream.send_json(r)

            except jsonapi.jsonmod.JSONDecodeError:
                m = "String: " + ''.join(message)
            print m

        return inner_function

    def send_units(self):
        for team_name, team in self.teams.items():
            to_send = []
            for unit in team.units:
                (x, y) = unit.coords
                name = unit.name
                to_send.append((name, (x, y)))
            r = {"state": "position_update",
                 "units": to_send}
            (p, stream, sock) = self.team_sockets[team_name]
            stream.send_json(r)

    def send_mesh(self):
        mesh_updates = self.world.get_mesh_serial()
        to_send = {"state": "mesh_update",
                   "updates": mesh_updates}
        for team_name in self.teams:
            (p, stream, sock) = self.team_sockets[team_name]
            stream.send_json(to_send)

    def send_steps(self):
        for team_name, team in self.teams.items():
            (p, stream, sock) = self.team_sockets[team_name]
            to_send = {"state": "steps",
                       "steps": team.get_steps()}
            stream.send_json(to_send)


def print_ready():
    print "Ready for connections"


if __name__ == "__main__":
    s = Server()
    print "Starting"
    s.ioloop.add_callback(print_ready)
    s.ioloop.start()
