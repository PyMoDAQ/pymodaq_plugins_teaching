import numpy as np

from pymodaq.control_modules.viewer_utility_classes import main
from pymodaq_data.data import DataCalculated

from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera

from pymodaq_plugins_teaching.hardware.beam import beam_properties


class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):
    """ Mock camera of a laser spot, extended to also return the position and size of the beam.

    It is the example of the post-processing done in `grab_data`: the raw image of the mock camera (the
    `DAQ_2DViewer_BSCamera` plugin of pymodaq_plugins_mockexamples) is analysed and the derived data are sent along
    with it, to be displayed, scanned or saved as any other data.

    * Compatible devices: the mock camera of pymodaq_plugins_mockexamples only.
    * Tested with: PyMoDAQ 5.3.x, Linux and Windows (against the mock camera).
    * Installation: needs pymodaq_plugins_mockexamples and laserbeamsize.
    """

    def grab_data(self, Naverage=1, **kwargs):
        dte = self.average_data(Naverage)
        image = dte.get_data_from_name('BSCamera').data[0]

        x, y, d_major, d_minor, _ = beam_properties(image)
        dte.append(DataCalculated('BeamSizeDXDY', data=[np.atleast_1d(d_major), np.atleast_1d(d_minor)],
                                  labels=['Dmajor', 'Dminor']))
        dte.append(DataCalculated('BeamSizeXY', data=[np.atleast_1d(x), np.atleast_1d(y)],
                                  labels=['X', 'Y']))
        self.dte_signal.emit(dte)


if __name__ == '__main__':
    main(__file__)
