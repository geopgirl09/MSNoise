"""
This script is responsible for rapidly scanning the data archive and
identifying the Networks/Stations and insert them in the *stations* table in
the database.

The ``data_folder`` (as defined in the configurator) is scanned expecting the
``data_structure`` and possible values are defined in *data_structures.py*:

.. code-block:: python
    
    data_structure['SDS'] = "YEAR/NET/STA/CHAN.TYPE/NET.STA.LOC.CHAN.TYPE.YEAR.DAY"
    data_structure['BUD'] = "NET/STA/STA.NET.LOC.CHAN.YEAR.DAY"
    data_structure['IDDS'] = "YEAR/NET/STA/CHAN.TYPE/DAY/NET.STA.LOC.CHAN.TYPE.YEAR.DAY.HOUR"
    data_structure['PDF'] = "YEAR/STA/CHAN.TYPE/NET.STA.LOC.CHAN.TYPE.YEAR.DAY"

For other structures, one has to edit the data_structures.py file and define
the reader in this script.

By default, station coordinates are initialized at 0.

.. note:: TODO: create a parser for stationXML and/or dataless SEED.

To run this script:

.. code-block:: sh

    $ msnoise populate
    
.. note:: TODO: add explanation how to make custom data_structure and parser

"""

import glob
import sys
import os
import numpy as np
from api import *

def main():
    db = connect()
    print
    print ">> Populating the Station table"
    print
    data_folder = get_config(db, 'data_folder')
    data_structure = get_config(db, 'data_structure')
    if data_structure in ["SDS", "IDDS"]:
        datalist = sorted(glob.glob(os.path.join(data_folder, "*", "*", "*")))
        stations = []
        for di in datalist:
            tmp = os.path.split(di)
            sta = tmp[1]
            net = os.path.split(tmp[0])[1]
            stations.append("%s_%s" % (net, sta))
        del datalist
    elif data_structure in ["BUD", ]:
        datalist = sorted(glob.glob(os.path.join(data_folder, "*", "*",)))
        stations = []
        for di in datalist:
            tmp = os.path.split(di)
            sta = tmp[1]
            net = os.path.split(tmp[0])[1]
            stations.append("%s_%s" % (net, sta))
        del datalist
    elif data_structure in ["PDF", ]:
        datalist = sorted(glob.glob(os.path.join(data_folder, "*", "*",)))
        stations = []
        for di in datalist:
            tmp = os.path.split(di)
            sta = tmp[1]
            net = get_config(db, 'network')
            stations.append("%s_%s" % (net, sta))
        del datalist
    else:
        print "Can't parse the archive for format %s !" % data_structure
        print "trying to import local parser (should return a station list)"
        print 
        try:
            sys.path.append(os.getcwd())
            from custom import populate
            stations = populate(data_folder)
        except:
            print "No file named custom.py in the %s folder" % os.getcwd()
            return
    stations = np.unique(stations)
    
    db = connect()
    for station in stations:
        net, sta = station.split('_')
        print 'Adding:', net, sta
        X = 0.0
        Y = 0.0
        altitude = 0.0
        coordinates = 'UTM'
        instrument = 'N/A'
        update_station(db, net, sta, X, Y, altitude,
                       coordinates=coordinates, instrument=instrument)
    return True

if __name__ == "__main__":
    main()