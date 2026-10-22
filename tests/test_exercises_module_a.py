"""Exercises of the module A: write the tests of the monochromator plugins (without hardware, no visible GUI)

The tests are skipped until you have written the plugins `daq_move_Monochromator.py` and
`daq_1Dviewer_Spectrometer.py` in this package (see the handout). Then replace each `...` by what the comment asks,
run `pytest tests/test_exercises_module_a.py` and the tests must go green.

The Spectrometer wrapper of the `hardware` folder is already a software simulation, so the plugins run against it.
The corrected tests are in the branch `correction-module-a`.
"""
import pytest

from pymodaq.utils.plugin_testing import make_actuator, make_detector, move_abs_and_wait, grab_and_wait

move_module = pytest.importorskip('pymodaq_plugins_teaching.daq_move_plugins.daq_move_Monochromator')
spectrometer_module = pytest.importorskip(
    'pymodaq_plugins_teaching.daq_viewer_plugins.plugins_1D.daq_1Dviewer_Spectrometer')


@pytest.fixture
def monochromator(qapp):
    plugin = make_actuator(move_module.DAQ_Move_Monochromator)
    assert plugin.initialized
    plugin.controller.homing_time = 0.3  # s: fast simulated referencing
    tau = plugin.settings.child('tau')
    tau.setValue(20.)  # ms: fast simulated movement
    plugin.commit_settings(tau)
    yield plugin
    plugin.close()


def test_move_abs(monochromator):
    """Exercise 1: move to 550 nm and check the position that is returned, in nm, within 0.5 nm"""
    pos = move_abs_and_wait(monochromator, 550.)
    assert ...  # check the units of `pos`
    assert ...  # check its value (hint: pos.value('nm') and pytest.approx)


def test_position_requests_during_homing_keep_the_last_value(monochromator):
    """Exercise 2: an instrument that is not referenced cannot answer; the plugin must keep the last known position"""
    move_abs_and_wait(monochromator, 500.)
    monochromator.controller.needs_referencing = True  # a more realistic instrument: it must be referenced
    monochromator.controller.find_reference()  # the referencing starts: the controller cannot answer any more
    pos = ...  # ask the plugin for its position (hint: get_actuator_value)
    assert ...  # the position is still 500 nm


def test_spectrum_has_a_wavelength_axis(qapp):
    """Exercise 3: grab a spectrum and check its dimension, its axis in nm and the finite values"""
    camera = make_detector(spectrometer_module.DAQ_1DViewer_Spectrometer)
    assert camera.initialized
    data = grab_and_wait(camera)[0]
    assert ...  # the data is 1D (hint: data.dim.name)
    assert ...  # the axis is in nm (hint: data.axes[0].units)
    assert ...  # axis and data have the same length (hint: camera.controller.Nx)
    camera.close()
