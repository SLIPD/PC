from rlrts_server import world
from itertools import repeat


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
    def __init__(self):
        self.state = "Initialization"

        # Use the data entered on the web interface to prepopulate things
        ## Populate teams from known set
        self.teams = {}
        for team in teams_connected:
            self.connect_team(team)

        ## Prepare unit names from known set
        self.remaining_names = []
        for key in teams:
            self.remaining_names.extend(zip(teams[key], repeat(key)))

        # Get data from network sources
        ## Receive world information from Pi
        (width, height) = 50, 50
        bx, by, bz = 125, 125, 20

        ## Setup the world
        self.setup_world((width, height), (bx, by, bz))

        ## Assign units
        for (device, coords) in devices:
            self.assign_unit(device, coords)

    def setup_world(self, (w, h), (bx, by, bz)):
        self.world = world.World((w, h), (bx, by, bz))
        for key in self.teams:
            self.teams[key].set_world(self.world)

    def assign_unit(self, device_id, (x, y)):
        (name, team_name) = self.remaining_names.pop()
        self.teams[team_name].add_unit(world.Unit(device_id, name, (x, y)))

    def connect_team(self, team_name):
        self.teams[team_name] = world.Team(team_name)

if __name__ == "__main__":
    s = Server()
