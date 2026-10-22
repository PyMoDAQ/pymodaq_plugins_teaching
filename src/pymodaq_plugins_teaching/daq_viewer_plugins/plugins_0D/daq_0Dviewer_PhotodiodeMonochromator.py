from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_0DViewer_PhotodiodeMonochromator(DAQ_Viewer_base):
    """ Instrument plugin class for the (mock) photodiode behind the monochromator of the teaching spectrometer.

    It returns the intensity of the spectrum at the central wavelength set by the monochromator actuator, hence both
    plugins have to share the same `Spectrometer` wrapper (master/slave mechanism).

    * Compatible devices: the `Spectrometer` mock wrapper of this package only.
    * Tested with: PyMoDAQ 5.3.x, Linux and Windows (against the wrapper and a fake controller, see tests/).
    * Installation: nothing to install, there is no driver.

    Attributes:
    -----------
    controller: Spectrometer
        The wrapper shared with the monochromator actuator
    """
    params = comon_parameters + [
        {'title': 'Infos:', 'name': 'info', 'type': 'str', 'value': '', 'readonly': True},
    ]

    def ini_attributes(self):
        self.controller: Spectrometer = None

    def commit_settings(self, param: Parameter):
        """No setting acts on the wrapper for this detector"""
        pass

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

        info = self.controller.infos
        self.settings.child('info').setValue(info)
        return info, initialized

    def close(self):
        """Terminate the communication, only if this plugin owns the controller"""
        if self.is_master and self.controller is not None:
            self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """Measure the intensity at the current central wavelength"""
        data_array = self.controller.grab_monochromator()
        self.dte_signal.emit(
            DataToExport(name='Photodiode',
                         data=[DataFromPlugins(name='Photodiode', data=[data_array],
                                               dim='Data0D', labels=['Intensity'])]))

    def stop(self):
        """Nothing to stop: the measurement is synchronous"""
        self.emit_status(ThreadCommand('Update_Status', ['Acquisition stopped']))
        return ''


if __name__ == '__main__':
    main(__file__)
