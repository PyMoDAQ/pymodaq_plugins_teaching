import numpy as np
from pymodaq.utils.data import DataFromPlugins
from qtpy.QtCore import QThread, Slot, QRectF
from qtpy import QtWidgets
import laserbeamsize as lbs

from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main

from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera


# TODO:
# (1) change the name of the following class to DAQ_2DViewer_TheNameOfYourChoice
# (2) change the name of this file to daq_2Dviewer_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_viewer_plugins/plugins_2D


class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):
    live_mode_available = False

    params = DAQ_2DViewer_BSCamera.params + [
        {'title': 'beam', 'name': 'beam', 'type': 'led', 'value': True},
        {'title': 'position', 'name': 'position', 'type': 'bool', 'value': True},
        {'title': 'width', 'name': 'width', 'type': 'bool', 'value': True},
        {'title': 'Beam Angle (deg)', 'name': 'phi2', 'type': 'bool', 'value': True },

    ]


    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        #########################################################"""
        data = self.average_data(Naverage)
        beam = data[0].data[0]

        x,y,d_major,d_minor,phi=lbs.beam_size(beam)
        #package things

        dte = DataToExport('BeamProfiler',
                           data=[
                               DataFromPlugins('Beam',
                                               data=[beam],
                                               labels=['Raw beam'],
                                               do_plot=self.settings['beam']),
                               DataFromPlugins('Position',
                                               data=[np.atleast_1d(x), np.atleast_1d(y)],
                                               labels=['x','y'],
                                               do_plot=self.settings['position']),
                               DataFromPlugins('Size',
                                              data=[np.atleast_1d(d_major), np.atleast_1d(d_minor)],
                                              labels=['Major', 'Minor'],
                                               do_plot=self.settings['width']),
                               DataFromPlugins('Angle',
                                               data=[np.atleast_1d(phi)],
                                               labels=['angle'],
                                               do_plot=self.settings['phi2']),
                           ])
        self.dte_signal.emit(dte)

       # return super().grab_data(Naverage=Naverage, **kwargs)


if __name__ == '__main__':
    main(__file__)
