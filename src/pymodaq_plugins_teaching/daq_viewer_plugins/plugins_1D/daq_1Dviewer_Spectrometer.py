from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_1DViewer_Spectrometer(DAQ_Viewer_base):
    """ Instrument plugin class for the (mock) camera of the teaching spectrometer.

    It returns the spectrum as a function of the wavelength axis, which depends on the central wavelength and on the
    grating of the monochromator actuator. Both plugins share the same `Spectrometer` wrapper (master/slave mechanism).

    * Compatible devices: the `Spectrometer` mock wrapper of this package only.
    * Tested with: PyMoDAQ 5.3.x, Linux and Windows (against the wrapper and a fake controller, see tests/).
    * Installation: nothing to install, there is no driver.

    Attributes:
    -----------
    controller: Spectrometer
        The wrapper, possibly shared with the monochromator actuator
    """
    params = comon_parameters + [
        {'title': 'Infos:', 'name': 'info', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Peak center (nm):', 'name': 'peak_center', 'type': 'float', 'value': 528.},
        {'title': 'Peak width (nm):', 'name': 'peak_width', 'type': 'float', 'value': 2., 'min': 0.1},
        {'title': 'Amplitude:', 'name': 'amplitude', 'type': 'float', 'value': 10., 'min': 0.},
        {'title': 'Noise:', 'name': 'noise', 'type': 'float', 'value': 0.5, 'min': 0.},
    ]

    def ini_attributes(self):
        self.controller: Spectrometer = None

    def commit_settings(self, param: Parameter):
        """Apply the change of a setting to the wrapper"""
        if param.name() == 'peak_center':
            self.controller.data_wavelength = param.value()
        elif param.name() == 'peak_width':
            self.controller.width = param.value()
        elif param.name() == 'amplitude':
            self.controller.amplitude = param.value()
        elif param.name() == 'noise':
            self.controller.noise = param.value()

    def ini_detector(self, controller=None):
        """Detector initialization

        Parameters
        ----------
        controller: Spectrometer
            The wrapper created by the master plugin (slave case), None in the master case
        """
        if self.is_master:
            self.controller = Spectrometer()
            initialized = self.controller.open_communication()
        else:
            self.controller = controller
            initialized = True

        self.settings.child('peak_center').setValue(self.controller.data_wavelength)
        self.settings.child('peak_width').setValue(self.controller.width)
        self.settings.child('amplitude').setValue(self.controller.amplitude)
        self.settings.child('noise').setValue(self.controller.noise)
        info = self.controller.infos
        self.settings.child('info').setValue(info)
        return info, initialized

    def close(self):
        """Terminate the communication, only if this plugin owns the controller"""
        if self.is_master and self.controller is not None:
            self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """Measure the spectrum on the wavelength axis of the current grating position"""
        spectrum = self.controller.grab_spectrum()
        axis = Axis('Wavelength', units='nm', data=self.controller.get_wavelength_axis(), index=0)
        self.dte_signal.emit(
            DataToExport(name='Spectrometer',
                         data=[DataFromPlugins(name='Spectrum', data=[spectrum], dim='Data1D',
                                               labels=['Intensity'], axes=[axis])]))

    def stop(self):
        """Nothing to stop: the measurement is synchronous"""
        self.emit_status(ThreadCommand('Update_Status', ['Acquisition stopped']))
        return ''


if __name__ == '__main__':
    main(__file__)
