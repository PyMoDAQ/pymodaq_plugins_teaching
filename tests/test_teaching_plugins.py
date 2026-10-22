"""Behaviour tests of the teaching spectrometer plugins (monochromator + photodiode + spectrum).

The `Spectrometer` wrapper of this package is already a software simulation of the instrument, so the real plugin
classes are run against it, without hardware and without visible GUI (see test_plugin_behaviour.py for the pattern
with a fake controller).
"""
import numpy as np
import pytest

from pymodaq.utils.plugin_testing import (make_actuator, make_detector, move_abs_and_wait, move_rel_and_wait,
                                          move_home_and_wait, grab_and_wait)

from pymodaq_plugins_teaching.daq_move_plugins.daq_move_Monochromator import DAQ_Move_Monochromator
from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_0D.daq_0Dviewer_PhotodiodeMonochromator import \
    DAQ_0DViewer_PhotodiodeMonochromator
from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_1D.daq_1Dviewer_Spectrometer import \
    DAQ_1DViewer_Spectrometer


def set_setting(plugin, name, value):
    """Change a setting and call commit_settings as the control module does when the user edits the tree"""
    param = plugin.settings.child(name)
    param.setValue(value)
    plugin.commit_settings(param)


@pytest.fixture
def monochromator(qapp):
    plugin = make_actuator(DAQ_Move_Monochromator)
    assert plugin.initialized
    set_setting(plugin, 'tau', 20.)  # ms, so that the simulated movement is fast
    yield plugin
    plugin.close()


class TestMonochromator:
    def test_value_has_units(self, monochromator):
        assert monochromator.get_actuator_value().units == 'nm'

    def test_move_abs(self, monochromator):
        pos = move_abs_and_wait(monochromator, 550.)
        assert pos.value('nm') == pytest.approx(550., abs=0.5)

    def test_move_rel(self, monochromator):
        move_abs_and_wait(monochromator, 500.)
        pos = move_rel_and_wait(monochromator, 20.)
        assert pos.value('nm') == pytest.approx(520., abs=0.5)

    def test_move_home(self, monochromator):
        move_abs_and_wait(monochromator, 500.)
        pos = move_home_and_wait(monochromator)
        assert pos.value('nm') == pytest.approx(600., abs=0.5)

    def test_grating_setting_reaches_the_wrapper(self, monochromator):
        set_setting(monochromator, 'grating', 'G1200')
        assert monochromator.controller.grating == 'G1200'

    def test_tau_setting_reaches_the_wrapper(self, monochromator):
        set_setting(monochromator, 'tau', 100.)
        assert monochromator.controller.tau == pytest.approx(0.1)


class TestDetectors:
    def test_photodiode_follows_the_monochromator(self, monochromator):
        photodiode = make_detector(DAQ_0DViewer_PhotodiodeMonochromator, controller=monochromator.controller)
        assert photodiode.controller is monochromator.controller
        move_abs_and_wait(monochromator, 528.)  # center of the simulated peak
        on_peak = grab_and_wait(photodiode)[0].data[0][0]
        move_abs_and_wait(monochromator, 600.)
        off_peak = grab_and_wait(photodiode)[0].data[0][0]
        assert on_peak > off_peak
        photodiode.close()
        assert monochromator.controller is not None  # only the master closes the shared wrapper

    def test_spectrum_has_a_wavelength_axis(self, qapp):
        camera = make_detector(DAQ_1DViewer_Spectrometer)
        assert camera.initialized
        dte = grab_and_wait(camera)
        data = dte[0]
        assert data.dim.name == 'Data1D'
        assert data.axes[0].units == 'nm'
        assert len(data.axes[0].get_data()) == len(data.data[0]) == camera.controller.Nx
        assert np.all(np.isfinite(data.data[0]))
        camera.close()

    def test_peak_center_setting_moves_the_peak(self, qapp):
        camera = make_detector(DAQ_1DViewer_Spectrometer)
        camera.controller.set_wavelength(528.)
        set_setting(camera, 'peak_center', 535.)
        assert camera.controller.data_wavelength == 535.
        camera.close()
