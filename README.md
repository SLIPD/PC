# SLIP D 2012 PC Software
This repository encompasses all of our software that will run on a PC
(Raspberry Pi, server, and client)


# Components

## Base station
The base station will repackage information from the devices and forward it to
the server; it will be careful to ensure that no duplicate data is sent to the
server. It will also repackage and forward packets from the server to the
devices.

## Game server
The game server will implement the logic of the game and ensure that each
client only receives the information they are allowed to have. It will also
forward input packets on to the base station.

## Client
The client will provide a visual representation of the state of the game as far
as the operator is allowed to know. It will also allow the operator to send
input back to the server to send commands to units.
