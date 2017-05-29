import os
import sys

from erosionbase import ErosionBase
from grass.script.core import run_command, parse_command

class ErosionUSLE(ErosionBase):

    def __init__(self, data, factors, epsg='5514', location_path=None,
                 computeStat=None, computeError=None):
        """USLE constructor.

        Two modes are available
         - creating temporal location, input data are imported

         - use existing location, in this case specified location must
           contain maps defined by self.maps directory

        :param epgs: EPSG code for creating new temporal location
        :param location_path: path to existing location
        """

        ErosionBase.__init__(self, epsg, location_path)

        self._computeStat = computeStat
        self._computeError = computeError

        # overwrite existing maps/files by default
        os.environ['GRASS_OVERWRITE']='1'

        self.euc_name = os.path.splitext(os.path.basename(data[0]))[0]
        self.dmt_name = os.path.splitext(os.path.basename(data[1]))[0]
        self.bpej_name = os.path.splitext(os.path.basename(data[2]))[0]
        self.lpis_name = os.path.splitext(os.path.basename(data[3]))[0]
        self.r_factor = factors[0]
        self.p_factor = factors[1]

        # internal input map names
        self._input = { 'euc' : self.euc_name,
                        'dmt' : self.dmt_name,
                        'bpej' : self.bpej_name,
                        'lpis' : self.lpis_name
        }
        # output names
        self._output = { 'erosion' : 'usle_g',
        }

    def computeStat(self, perc, label):
        if self._computeStat is not None:
            self._computeStat.emit(perc, label)
        sys.stderr.write('[pyerosion] {}: {}\n'.format(perc, label))

    def computeError(self, label):
        if self._computeError is not None:
            self._computeError.emit(label)
        sys.stderr.write('[pyerosion ERROR]: {}\n'.format(label))

    def run(self, terraflow=False):
        """
        Erosion computing
        :param terraflow: True : computing direction by method terraflow
                                    False : computing direction by method wattershed
        """
        # set computation region based on input DMT
        try:
            self.computeStat(10, u'Setting up computation region...')
            reg = parse_command('g.region',
                                raster=self._input['dmt'],
                                flags='g'
            )
        except:
            self.computeError(u'Error in setting up computation region.')
            return
        # computing slope on input DMT
        try:
            self.computeStat(15, u'Computing slope...')
            slope = self._temp_map('raster')
            run_command('r.slope.aspect',
                        elevation=self._input['dmt'],
                        slope=slope
            )
        except:
            self.computeError(u'Error in computing slope.')
            return
        # setting up mask
        try:
            self.computeStat(20, u'Setting up mask...')
            run_command('r.mask',
                        vector=self._input['euc']
            )
        except:
            self.computeError(u'Error in setting up mask.')
            return
        # computing accumulation
        try:
            # TODO: discuss accumulation computation (which module, use
            # filled DMT?)
            self.computeStat(25, u'Computing accumulation...')
            accu = self._temp_map('raster')
            if terraflow:
                dmt_fill = self._temp_map('raster')
                direction = self._temp_map('raster')
                swatershed = self._temp_map('raster')
                tci = self._temp_map('raster')
                run_command('r.terraflow',
                            elevation=self._input['dmt'],
                            filled=dmt_fill,
                            direction=direction,
                            swatershed=swatershed,
                            accumulation=accu,
                            tci=tci
                )
            else:
                run_command('r.watershed',
                            flags='a',
                            elevation=self._input['dmt'],
                            accumulation=accu
                )
        except:
            self.computeError(u'Error in computing accumulation.')
            return
        #  computing LS Factor
        try:
            self.computeStat(40, u'Computing LS factor...')
            formula='ls = 1.6 * pow(' + accu + '* (' + reg['nsres'] +' / 22.13), 0.6) * pow(sin(' + \
            slope + '* (3.1415926/180)) / 0.09, 1.3)'
            run_command('r.mapcalc',
                        expr=formula
            )
        except:
            self.computeError(u'Error in computing LS factor.')
            return
        # computing KC Factor
        try:
            self.computeStat(60, u'Computing KC factor...')
            # overlay layers: bpej and lpis
            bpej_lpis = self._temp_map('vector')
            run_command('v.overlay',
                        ainput=self._input['bpej'],
                        binput=self._input['lpis'],
                        operator='or',
                        output=bpej_lpis
            )
            # add column KC
            run_command('v.db.addcolumn',
                        map=bpej_lpis,
                        columns='KC double'
            )
            # compute KC value
            run_command('v.db.update',
                        map=bpej_lpis,
                        column='KC',
                        query_column='a_K * b_C')
        except:
            self.computeError(u'Error in computing KC factor.')
            return
        # compute final G Factor (Erosion factor)
        try:
            self.computeStat(75, u'Computing Erosion factor...')
            bpej_lpis_raster=self._temp_map('raster')
            run_command('v.to.rast',
                        input=bpej_lpis,
                        output=bpej_lpis_raster,
                        use='attr',
                        attribute_column='KC',
                        where='KC IS NOT NULL'
            )
            usle=self._output['erosion'] + '=' + self.r_factor + '* ls *' + bpej_lpis_raster + '*' + self.p_factor
            run_command('r.mapcalc',
                        expr=usle
            )
            run_command('r.colors',
                        flags='ne',
                        map=self._output['erosion'],
                        color='corine'
            )
        except:
            self.computeError(u'Error in computing Erosion factor.')
            return

    def test(self):
        """
        Run test.

        - prints output erosion map metadata
        """
        run_command('g.gisenv')
        run_command('r.univar', map=self._output['erosion'])
