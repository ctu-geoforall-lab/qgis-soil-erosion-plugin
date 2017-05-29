# TODO: header

import os
import sys
import subprocess
import shutil
import tempfile
import binascii

class ErosionError(StandardError):
    pass

def findGRASS():
    """Find GRASS.

    Find location of GRASS.

    :todo: Avoid bat file calling.
    """
    ########### SOFTWARE
    if sys.platform == 'win32':
        qgis_prefix_path = os.environ['QGIS_PREFIX_PATH']
        bin_path = os.path.join(os.path.split(
            os.path.split(qgis_prefix_path)[0])[0],
            'bin'
        )
        grass7bin = None
        for grass_version in ['70', '72']:
            gpath = os.path.join(bin_path, 'grass{}.bat'.format(grass_version))
            if os.path.exists(gpath):
                grass7bin = gpath
                break

        if grass7bin is None:
            raise ImportError("No grass70.bat or grass72.bat found.")
    else:
        grass7bin = '/usr/bin/grass'
    startcmd = [grass7bin, '--config', 'path']

    p = subprocess.Popen(startcmd,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if p.returncode != 0:
        raise ImportError("Reason: ({cmd}: {reason})".format(
            cmd=startcmd, reason=err)
        )

    str_out = out.decode("utf-8")
    gisbase = str_out.rstrip(os.linesep)

    # Set GISBASE environment variable
    os.environ['GISBASE'] = gisbase
    # define GRASS-Python environment
    sys.path.append(os.path.join(gisbase, "etc", "python"))

    return grass7bin

try:
    grass7bin = findGRASS()
except (StandardError, ImportError) as e:
    raise ImportError('Unable to find GRASS installation. {}'.format(e))

temp_dir = None
import grass.script as gscript
from grass.script import setup as gsetup
from grass.exceptions import ScriptError, CalledModuleError
from osgeo import ogr, gdal

class ErosionBase():
    def __init__(self, epsg='5514', location_path=None):
        """USLE constructor.

        Two modes are available
         - creating temporal location, input data are imported

         - use existing location, in this case specified location must
           contain maps defined by self.maps directory

        :param epsg: EPSG code for creating new temporal location
        :param location_path: path to existing location
        """
        self.file_type = None
        self.grass_layer_types = {}

        if not location_path:
            gisdb = os.path.join(tempfile.gettempdir(), 'grassdata')
            if not os.path.isdir(gisdb):
                os.mkdir(gisdb)

            # location/mapset: use random names for batch jobs
            string_length = 16
            location = binascii.hexlify(os.urandom(string_length))
            mapset   = 'PERMANENT'
            temp_dir = gisdb

            self.temporal_location = True
        else:
            dirname, mapset = os.path.split(location_path.rstrip(os.path.sep))
            gisdb, location = os.path.split(dirname)
            self.temporal_location = False

        # GRASS session must be initialized first
        gsetup.init(os.environ['GISBASE'], gisdb, location, mapset)
        # Create temporal location if requested 
        if not location_path:
            try:
                gscript.create_location(gisdb, location, epsg, overwrite=True)
            except ScriptError as e:
                raise ErosionError('{}'.format(e))

        # Be quiet, print only error messages
        os.environ['GRASS_VERBOSE'] = '0'

        # Manage temporal maps
        self._temp_maps = []
        self._map_counter = 0
        self._pid = os.getpid()

    def __del__(self):
        """Destructor.

        - deleting temporal location
        """
        if self.temporal_location:
            return

        for map_name, map_type in self._temp_maps:
            gscript.run_command('g.remove', flags='f', type=map_type, name=map_name)

    def location_path(self):
        ge = gscript.gisenv()

        return os.path.join(ge['GISDBASE'], ge['LOCATION_NAME'])

    def import_data(self, files):
        """
        Define name and type imported files
        
        :param files: Imported files
        """
        for file_name in files:
            file_type = self._file_type_test(file_name)
            self.import_file(file_name, file_type)

    def import_file(self, file_name, file_type):
        """
        Import files
        
        :param file_name: name of file
        :param file_type: type of file (raster, vector, table)
        """
        map_name = os.path.splitext(os.path.basename(file_name))[0]
        if map_name in self.grass_layer_types:
            return # TODO: how to handler raster and vector map with the same name
        # import
        try:
            if file_type == 'raster':
                gscript.run_command('r.external', input=file_name, output=map_name)
            elif file_type == 'vector':
                gscript.run_command('v.in.ogr', input=file_name, output=map_name)
            elif file_type == 'table':
                gscript.run_command('db.in.ogr', input=file_name, output=map_name)
            else:
                raise ErosionError("Unknown file type")
        except CalledModuleError as e:
            raise ErosionError('{}'.format(e))

        self.grass_layer_types[map_name] = file_type

    def test(self):
        """
        Run test.

        - prints messages
        """
        print('Current GRASS GIS 7 environment:')
        print(gscript.gisenv())

        print('Available raster maps:')
        for rast in gscript.list_strings(type = 'rast'):
            print('{}{}'.format(' ' * 4, rast))

        print('Available vector maps:')
        for vect in gscript.list_strings(type = 'vect'):
            print('{}{}'.format(' ' * 4, vect))

    def export_data(self, outdir):
        """
        Export data

        :param grass_file: File for output
        :param o_path: Path to output file
        :param o_name: Name of output file
        """
        for k, v in iter(self._output.items()):
            print ("Exporting '{}'".format(v))
            # determine map type
            if gscript.find_file(name=v, element='cell')['fullname']:
                # raster detected
                gscript.run_command('g.region',
                                    raster=v)
                gscript.run_command('r.out.gdal',
                                    input=v,
                                    output=os.path.join(outdir, v + '.tif'))
            elif gscript.find_file(name=v, element='vector')['fullname']:
                # vector detected
                gscript.run_command('v.out.ogr',
                                    flags='sm',
                                    input=v,
                                    output=os.path.join(outdir, v + '.shp'))
            else:
                pass # TODO: warning

    def _file_type_test(self, filename):
        """
        Run type test

        return type of input test file 

        :param filename: Name of input test file
        """
        # vector test
        src_ds = ogr.Open(filename)
        if src_ds is not None:
            if '.csv' in filename:
                return 'table'
            else:
                return 'vector'
        # raster test
        src_ds = gdal.Open(filename)
        if src_ds is not None:
            return 'raster'

        if src_ds is None:
            raise ErosionError("File '{}' not found".format(filename))

        raise ErosionError("Unknown file type")

    def _temp_map(self, map_type):
        """
        Define name and type of temporal maps
        """
        map_name = 'map_{}_{}'.format(self._map_counter, self._pid)
        self._temp_maps.append((map_name, map_type))
        self._map_counter += 1
        
        return map_name
    
