import numpy as np


from pymodaq_utils.math_utils import gauss1D
from typing import List, Union
from collections.abc import Iterable
from numbers import Number
import math
from time import perf_counter


class NotReferencedError(RuntimeError):
    """Raised by the spectrometer when it is asked something while its grating is being referenced (homing)"""


class Spectrometer:
    """Mock Controller of a spectrometer

    Allows to change the used grating, to move the grating by setting the central wavelength and get the data out of it

    By default the grating is referenced at once (`find_reference` is instantaneous). Set `needs_referencing` to True
    for a more realistic instrument: as on many real instruments, the grating position is then unknown while it is
    being referenced (`find_reference`), and the position, the movements and the data raise a `NotReferencedError`
    until `is_referenced` is True again.
    """
    needs_referencing = False  # True: the referencing takes `homing_time` and the instrument cannot answer meanwhile
    gratings = ['G300', 'G1200']
    reference_wavelength = 600.  # nm, position of the reference (limit) of the grating
    homing_time = 1.5  # s, duration of the referencing

    satellite_lines = False  # True: weaker lines are added at the hidden positions of `satellite_positions`
    satellite_positions = ((470., 0.15), (590., 0.10))  # (position in nm, amplitude relative to the main line)
    intensity_drift = False  # True: the intensity oscillates slowly with the number of measurements
    drift_depth = 0.2  # relative amplitude of the intensity drift
    drift_period = 37.3  # period of the intensity drift, in number of measurements

    Nx = 256
    infos = 'Spectrometer Controller Wrapper 0.1.0'

    def __init__(self):
        super().__init__()

        self._amp = 10
        self._noise = 0.5
        self._wh = 2
        self._grating = self.gratings[0]

        self._tau = 2  # s
        self._alpha = None
        self._init_value = None
        self._start_time = 0
        self._moving = False
        self._espilon = 0.01

        self._lambda = 532
        self._target_lambda = self._lambda

        self._lambda0 = 528

        self._homing_start = None  # time at which the referencing started, None if not referencing
        self._n_measurements = 0  # number of calls to the response, drives the intensity drift

    def open_communication(self):
        return True

    def close_communication(self):
        return True

    def stop(self):
        self._moving = False

    @property
    def tau(self):
        """
        fetch the characteristic time to reach a particular wavelength
        Returns
        -------
        float: the current characteristic decay time value

        """
        return self._tau

    @tau.setter
    def tau(self, value):
        """
        Set the characteristic time to reach a particular wavelength
        Parameters
        ----------
        value: (float) a strictly positive characteristic time in seconds
        """
        if value <= 0:
            raise ValueError(f'A characteristic time of {value} is not possible. It should be strictly positive')
        else:
            self._tau = value

    @property
    def grating(self):
        """Get.set the current grating in the spectrometer"""
        return self._grating

    @grating.setter
    def grating(self, grat):
        if grat in self.gratings:
            self._grating = grat

    @property
    def amplitude(self):
        """Get/Set the amplitude of the measured spectrum"""
        return self._amp

    @amplitude.setter
    def amplitude(self, value):
        if value > 0.:
            self._amp = value
        if value > 100:
            self._amp = 100

    @property
    def noise(self):
        """Get/Set the noise of the measured spectrum"""
        return self._noise

    @noise.setter
    def noise(self, value):
        if value > 0.:
            self._noise = value

    @property
    def width(self):
        """Get/Set the width of the measured spectrum main peak"""
        return self._wh

    @width.setter
    def width(self, value):
        if value > 0.:
            self._wh = value

    @property
    def is_referenced(self) -> bool:
        """False while the grating is being referenced (`find_reference` started and not yet finished)"""
        if self._homing_start is not None and perf_counter() - self._homing_start >= self.homing_time:
            self._homing_start = None
            self._moving = False
            self._lambda = self._target_lambda = self.reference_wavelength
        return self._homing_start is None

    def _check_referenced(self):
        if not self.is_referenced:
            raise NotReferencedError('The spectrometer is being referenced, its position is not available yet')

    def find_reference(self):
        """Start the referencing of the grating on its limit, for absolute positioning (non blocking)

        Without `needs_referencing` the grating is on its reference at once. Otherwise the referencing takes
        `homing_time`: until it ends, `is_referenced` is False and the other methods raise a `NotReferencedError`:
        poll `get_wavelength` (or `is_referenced`) to know when it is finished.
        """
        self._moving = False
        if not self.needs_referencing:
            self._lambda = self._target_lambda = self.reference_wavelength
            return
        self._homing_start = perf_counter()

    def set_wavelength(self, value, set_type='abs'):
        """Move the grating to set the central wavelength out of the spectrometer"""
        self._check_referenced()
        if set_type == 'abs' and value < 0:
            raise ValueError('Wavelength cannot be negative')
        if set_type == 'abs':
            self._target_lambda = value
        else:
            self._target_lambda = self._lambda + value

        self._init_value = self._lambda
        if self._init_value != self._target_lambda:
            self._alpha = math.fabs(math.log(self._espilon / math.fabs(self._init_value - self._target_lambda)))
        else:
            self._alpha = math.fabs(math.log(self._espilon / 10))
        self._start_time = perf_counter()
        self._moving = True

    def get_wavelength(self):
        """Get the current central wavelength in the spectrometer

        Raises
        ------
        NotReferencedError: while the grating is being referenced
        """
        self._check_referenced()
        if self._moving:
            curr_time = perf_counter()
            self._lambda = \
                math.exp(- self._alpha * (curr_time-self._start_time) / self._tau) *\
                (self._init_value - self._target_lambda) + self._target_lambda
        return self._lambda

    def get_wavelength_axis(self):
        """Get the wavelength axis out of the spectrometer (dependent of the central wavelength (grating position))
        and dispersion of the selected grating"""
        self._check_referenced()
        if self._grating == 'G300':
            coeff = 0.7
        elif self._grating == 'G1200':
            coeff = 0.25
        return (np.linspace(0, self.Nx, self.Nx, endpoint=False) - self.Nx / 2) * coeff + self._lambda

    @property
    def data_wavelength(self,):
        """Central wavelength of the physical feature measured by our spectrometer"""
        return self._lambda0

    @data_wavelength.setter
    def data_wavelength(self, lambda0):
        """Defines the center wavelength of the spectrum peak to be measured"""
        if lambda0 < 0:
            raise ValueError('Wavelength cannot be negative')
        self._lambda0 = lambda0

    def _set_data_response(self, lambda_axis: Union[float, Iterable] = 515.) -> np.ndarray:
        """Defines the wavelength response of the physical process measured by our spectrometer

        Parameters
        ----------
        lambda_axis: float or iterable of floats

        Returns
        -------
        ndarray
        """
        if isinstance(lambda_axis, Number):
            lambda_axis = np.array([lambda_axis])
        else:
            if not isinstance(lambda_axis, Iterable):
                raise TypeError('lambda_axis should be an iterable of float')
            else:
                if not isinstance(lambda_axis[0], Number):
                    raise TypeError('lambda_axis should be an iterable of float')

        width = self._wh * (1 + self._amp/10)
        response = (self._amp * gauss1D(lambda_axis, self._lambda0, width)
                    * (1+0.5 * np.sin(self._amp/10) * np.sin((lambda_axis-self._lambda0) / (self._wh))))
        if self.satellite_lines:
            for position, relative_amplitude in self.satellite_positions:
                response = response + self._amp * relative_amplitude * gauss1D(lambda_axis, position, width)
        if self.intensity_drift:
            response = response * (1 + self.drift_depth * np.sin(2 * np.pi * self._n_measurements / self.drift_period))
        self._n_measurements += 1
        return response + self._noise * np.random.rand(len(lambda_axis))

    def _get_data_0D(self, data=None):
        """Get the data at the central wavelength of the spectrometer"""
        if data is None:
            data = self._set_data_response(self.get_wavelength())
        return data

    def _get_data_1D(self, data=None):
        """Get the data as a function of the wavelength axis of the spectrometer
        """
        if data is None:
            data = self._set_data_response(self.get_wavelength_axis())
        return data

    def grab_spectrum(self):
        """get the intensity spectrum out of the spectrometer"""
        return self._get_data_1D()

    def grab_image(self):
        y_axis_array = np.linspace(0, 127, 128)
        data1D = self._get_data_1D()
        data2D = np.outer(gauss1D(y_axis_array, np.mean(y_axis_array), 50), data1D)
        return data2D

    def grab_monochromator(self):
        """get the intensity at the central wavelength"""
        return self._get_data_0D()
