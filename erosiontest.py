#!/usr/bin/env python

import os
import sys

sys.path.insert(0, r'C:\Users\sanko\Documents\GitHub\bp-novotny-2017')
from pyerosion import erosionusle

reload(erosionusle)
location = r'D:\GRASSDATA\USLE\PERMANENT'
if len(sys.argv) > 1:
    location=sys.argv[1]

er = erosionusle.ErosionUSLE(location_path=location)
# http://training.gismentors.eu/geodata/qgis/
if location is None:
    home = os.path.expanduser("~")
    er.import_files([os.path.join(home, 'geodata', 'hydrologie', 'dmt.tif'),
                     os.path.join(home, 'geodata', 'hydrologie', 'vzorek1', 'hpj.shp'),
                     os.path.join(home, 'geodata', 'hydrologie', 'vzorek1', 'kpp.shp'),
                     os.path.join(home, 'geodata', 'hydrologie', 'vzorek1', 'landuse.shp')]
    )
er.run()
er.test()

