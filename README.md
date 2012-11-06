# SLIP D 2012 PC Software
This repository encompasses all of our software that will run on a PC
(server and client)

# Running
The expected way to acquire the libraries required for this will be to create a
virtualenv by running:

`virtualenv rlrts.env`

Then you will activate the virtualenv with

`source rlrts.env/bin/activate` on linux

and you will install the requirements with

`pip install -r requirements.txt`.

This should make python work adequately


# Components

## Game server
The game server will implement the logic of the game and ensure that each
client only receives the information they are allowed to have. It will also
forward input packets on to the base station.

## Client
The client will provide a visual representation of the state of the game as far
as the operator is allowed to know. It will also allow the operator to send
input back to the server to send commands to units.
