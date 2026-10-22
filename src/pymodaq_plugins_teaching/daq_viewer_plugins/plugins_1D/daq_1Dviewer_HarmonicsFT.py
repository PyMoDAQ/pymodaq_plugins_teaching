from pymodaq.control_modules.viewer_utility_classes import main
from pymodaq_data.data import DataToExport, Axis
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_1D.daq_1Dviewer_Harmonics import DAQ_1DViewer_Harmonics


class DAQ_1DViewer_HarmonicsFT(DAQ_1DViewer_Harmonics):
    """ The harmonics spectrum of pymodaq_plugins_mockexamples, plus its Fourier transform.

    Inheritance at work: the parameters, the initialisation and the controller come from the parent plugin, only
    `grab_data` is rewritten to send the modulus of the Fourier transform (`DataWithAxes.ft`) along with the spectrum.

    * Compatible devices: the Harmonics generator of pymodaq_plugins_mockexamples only.
    * Tested with: PyMoDAQ 5.3.x, Linux and Windows (against the mock generator).
    * Installation: needs pymodaq_plugins_mockexamples.
    """

    def grab_data(self, Naverage=1, **kwargs):
        spectrum = self.controller.get_spectrum()
        axis = self.controller.get_axis()
        dwa = DataFromPlugins(name='Harmonics', data=[spectrum.magnitude], dim='Data1D', labels=['Spectrum'],
                              units=str(spectrum.units),
                              axes=[Axis(label='Energy', units=str(axis.units), data=axis.magnitude)])
        dwa_ft = dwa.ft().abs()
        dwa_ft.name = 'HarmonicsFT'
        self.dte_signal.emit(DataToExport('Harmonics', data=[dwa, dwa_ft]))


if __name__ == '__main__':
    main(__file__, 'HarmonicsFT')
