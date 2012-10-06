#!/usr/bin/env python2
import serial
from time import sleep
import sys

import nmea

serial = serial.Serial(sys.argv[1], baudrate=9600, timeout=1.0)

print "===Connected==="
time = ""
lat = lng = ''
ns = ew = ''

while True:
    try:
        data = serial.readline()

        #print data[:-1]
        nmea_type = nmea.parseLine(data)
        if nmea_type in ("GGA", "RMC"):
            time = nmea.data['UtcTime']
            (lat, lng) = nmea.data['Latitude'], nmea.data['Longitude']
            (ns, ew) = nmea.data['NsIndicator'], nmea.data['EwIndicator']

        if nmea_type in ("RMC"):
            pass

        sys.stdout.write('\rTime: %s  Lat, Lng: %s%s, %s%s                  ' %
                (time, lat, ns, lng, ew))
        sys.stdout.flush()
    except KeyboardInterrupt:
        serial.close()
        break
    except ValueError:
        pass
    except AssertionError:
        pass
    except TypeError:
        pass
    except KeyError:
        pass

print "===Disconnected==="
