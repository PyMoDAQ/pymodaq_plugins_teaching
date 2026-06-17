import numpy as np
from pymodaq.control_modules.viewer_utility_classes import main
from pymodaq_data import DataCalculated, DataToExport

from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera

import laserbeamsize as lbs


class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):

    def grab_data(self, Naverage=1, **kwargs):
        dte = self.average_data(Naverage)

        data_array_2D = dte.get_data_from_name('BSCamera')[0]
        #calculation
        x, y, d_major, d_minor, phi = lbs.beam_size(data_array_2D)

        data_0D = DataCalculated('BeamSizeDXDY',
                                 data=[np.atleast_1d(d_major),
                                       np.atleast_1d(d_minor),],
                                 labels=['Dmajor', 'Dminor'],)
        data_0D_position = DataCalculated('BeamSizeXY',
                                          data=[np.atleast_1d(x),
                                                np.atleast_1d(y),],
                                          labels=['X', 'Y'],)

        #emission
        dte.append(data_0D)
        dte.append(data_0D_position)
        self.dte_signal.emit(dte)


if __name__ == '__main__':
    main(__file__)
