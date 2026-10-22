from time import perf_counter, sleep
from typing import Union, List, Dict

from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)
from pymodaq.control_modules.daq_move_ui.utils import UiType
from pymodaq_utils.utils import ThreadCommand
from pymodaq_gui.parameter import Parameter
from pymodaq_data import Q_

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_Move_Monochromator(DAQ_Move_base):
    """ Instrument plugin class for the (mock) monochromator of the teaching spectrometer.

    The actuator sets the central wavelength of the grating of the `Spectrometer` wrapper. There is no hardware: the
    wrapper simulates the movement of the grating.

    * Compatible devices: the `Spectrometer` mock wrapper of this package only.
    * Tested with: PyMoDAQ 5.3.x, Linux and Windows (against the wrapper and a fake controller, see tests/).
    * Installation: nothing to install, there is no driver.

    Attributes:
    -----------
    controller: Spectrometer
        The wrapper shared with the detectors of the spectrometer (master/slave mechanism)
    """
    is_multiaxes = False
    _axis_names: Union[List[str], Dict[str, int]] = ['Wavelength']
    _controller_units: Union[str, List[str]] = 'nm'
    _epsilons: Union[float, List[float]] = 0.1
    data_actuator_type = DataActuatorType.DataActuator
    ui_type = UiType.NONE
    has_encoder = True
    HOME_TIMEOUT_S = 30.  # maximum time to wait for the end of the homing movement

    params = [
        {'title': 'Infos:', 'name': 'info', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Grating:', 'name': 'grating', 'type': 'list',
         'limits': Spectrometer.gratings, 'value': Spectrometer.gratings[0]},
        {'title': 'Tau (ms):', 'name': 'tau', 'type': 'float', 'value': 500., 'min': 1.},
    ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilons)

    def ini_attributes(self):
        self.controller: Spectrometer = None

    def get_actuator_value(self) -> DataActuator:
        """Get the current central wavelength, with the scaling applied"""
        pos = DataActuator(data=self.controller.get_wavelength(), units=self.axis_unit)
        pos = self.get_position_with_scaling(pos)
        return pos

    def close(self):
        """Terminate the communication, only if this plugin owns the controller"""
        if self.is_master and self.controller is not None:
            self.controller.close_communication()

    def commit_settings(self, param: Parameter):
        """Apply the change of a setting to the wrapper"""
        if param.name() == 'tau':
            self.controller.tau = Q_(param.value(), 'ms').m_as('s')
        elif param.name() == 'grating':
            self.controller.grating = param.value()

    def ini_stage(self, controller=None):
        """Actuator initialization

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

        self.settings.child('tau').setValue(Q_(self.controller.tau, 's').m_as('ms'))
        self.settings.child('grating').setValue(self.controller.grating)
        info = self.controller.infos
        self.settings.child('info').setValue(info)
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move to the absolute central wavelength defined by value"""
        value = self.check_bound(value)
        self.target_value = value
        value = self.set_position_with_scaling(value)
        self.controller.set_wavelength(value.value(self.axis_unit))

    def move_rel(self, value: DataActuator):
        """ Move by the relative wavelength defined by value"""
        value = self.check_bound(self.current_value + value) - self.current_value
        self.target_value = value + self.current_value
        value = self.set_position_relative_with_scaling(value)
        self.controller.set_wavelength(value.value(self.axis_unit), set_type='rel')

    def move_home(self):
        """Go to the reference wavelength, and tell PyMoDAQ when it is reached

        PyMoDAQ does not poll the position after a home move: the plugin has to call `move_done` itself once the
        homing is finished. Here the wrapper simulates a slow movement, so wait for it (with a timeout).
        """
        self.controller.find_reference()
        t0 = perf_counter()
        while (abs(self.controller.get_wavelength() - self.controller.target_wavelength) > self.epsilon
               and perf_counter() - t0 < self.HOME_TIMEOUT_S):
            sleep(0.01)
        self.move_done()

    def stop_motion(self):
        """Stop the grating"""
        self.controller.stop()
        self.emit_status(ThreadCommand('Update_Status', ['Motion stopped']))


if __name__ == '__main__':
    main(__file__)
