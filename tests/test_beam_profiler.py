"""Tests of the beam profiler of the module B: analysis function, 2D plugin, standalone app and Dashboard extension"""
import time

import numpy as np
import pytest
from qtpy import QtWidgets

from pymodaq.utils.plugin_testing import make_detector, grab_and_wait, loaded_extension, PluginExtensionChecks
from pymodaq.control_modules.enums import DAQTypesEnum
from pymodaq_data.data import DataRaw, DataToExport, Axis
from pymodaq_gui import utils as gutils

from pymodaq_plugins_teaching.hardware.beam import beam_properties, gaussian_beam_image
from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BeamProfiler import \
    DAQ_2DViewer_BeamProfiler
from pymodaq_plugins_teaching.extensions.beam_profiler import BeamProfiler
from pymodaq_plugins_teaching.app.beam_profiler_app import BeamProfilerApp


class TestExtensionsLoad(PluginExtensionChecks):
    """One loading test per extension of the package (provided by PyMoDAQ)"""
    strict_imports = True


class TestAnalysis:
    def test_rotated_beam(self):
        image = gaussian_beam_image(center=(150., 100.), size=(60., 30.), angle=30.)
        x, y, d_major, d_minor, phi = beam_properties(image)
        assert (x, y) == (pytest.approx(150., abs=1.), pytest.approx(100., abs=1.))
        assert d_major == pytest.approx(60., rel=0.03)
        assert d_minor == pytest.approx(30., rel=0.03)
        assert np.rad2deg(phi) == pytest.approx(30., abs=1.)

    def test_beam_properties_of_a_simulated_beam(self):
        image = gaussian_beam_image(center=(150., 100.), size=(40., 20.), angle=0.)
        x, y, d_major, d_minor, _ = beam_properties(image)
        assert x == pytest.approx(150., abs=1.)
        assert y == pytest.approx(100., abs=1.)
        assert d_major == pytest.approx(40., rel=0.05)
        assert d_minor == pytest.approx(20., rel=0.05)


def test_plugin_sends_the_beam_properties(qapp):
    camera = make_detector(DAQ_2DViewer_BeamProfiler)
    assert camera.initialized
    dte = grab_and_wait(camera)
    names = dte.get_names()
    assert {'BSCamera', 'BeamSizeDXDY', 'BeamSizeXY'} <= set(names)
    d_major, d_minor = dte.get_data_from_name('BeamSizeDXDY').data
    assert d_major[0] >= d_minor[0] > 0
    camera.close()


def _beam_dte(**kwargs) -> DataToExport:
    image = gaussian_beam_image(**kwargs)
    dwa = DataRaw('Camera', data=[image], dim='Data2D',
                  axes=[Axis('y', 'pixel', data=np.arange(image.shape[0]), index=0),
                        Axis('x', 'pixel', data=np.arange(image.shape[1]), index=1)])
    return DataToExport('camera', data=[dwa])


def test_extension_shows_the_beam_properties(qapp):
    with loaded_extension(BeamProfiler) as (dashboard, extension):
        extension.show_data(_beam_dte(center=(120., 80.), size=(50., 30.)))
        assert extension._quit_fun() is True


def test_extension_without_camera_does_not_fail(qapp):
    with loaded_extension(BeamProfiler) as (dashboard, extension):
        extension.grab()  # no experiment loaded, no camera: only a message in the status bar


def test_app_simulates_and_analyses(qapp):
    dockarea = gutils.DockArea()
    app = BeamProfilerApp(dockarea)
    app.simulate()
    app.settings.child('size_x').setValue(60.)  # triggers value_changed, then a new simulation
    dockarea.close()


def _wait_for(condition, timeout=10.):
    t0 = time.perf_counter()
    while not condition() and time.perf_counter() - t0 < timeout:
        QtWidgets.QApplication.processEvents()
        time.sleep(0.01)
    return condition()


@pytest.fixture
def extension_with_camera(qapp):
    """The extension loaded in a Dashboard holding the BeamProfiler camera, initialized (no visible GUI)"""
    with loaded_extension(BeamProfiler) as (dashboard, extension):
        camera = dashboard.add_det('Camera', DAQTypesEnum.DAQ2D, 'BeamProfiler')
        camera.init_hardware_ui(True)
        assert _wait_for(lambda: camera.initialized_state)
        extension.modules_manager.add_modules([camera])
        extension.settings.child('camera').setLimits(extension.modules_manager.detectors_name)
        extension.settings.child('camera').setValue('Camera')
        assert extension.modules_manager.selected_detectors_name == ['Camera']
        shown = []
        extension.lcd.setvalues = lambda values, **kwargs: shown.append(values)
        yield extension, shown
        extension.set_live(False)
        camera.quit_fun()


def test_extension_grabs_asynchronously_through_the_modules_manager(extension_with_camera):
    extension, shown = extension_with_camera
    extension.grab()
    assert _wait_for(lambda: len(shown) == 1)
    d_major, d_minor = shown[0][2][0], shown[0][3][0]
    assert d_major >= d_minor > 0
    assert not extension._grabbing  # the grab is finished and its callback forgotten


def test_extension_live_mode_chains_the_grabs(extension_with_camera):
    extension, shown = extension_with_camera
    extension.settings.child('refresh').setValue(20)
    extension.set_live(True)
    assert _wait_for(lambda: len(shown) >= 3)
    extension.set_live(False)
    n_after_stop = len(shown)
    _wait_for(lambda: False, timeout=0.3)
    assert len(shown) <= n_after_stop + 1  # at most the grab that was already running


def test_actions_use_material_icons(qapp):
    """The examples only use MaterialIcons (not the old png of the icon library), the ones PyMoDAQ themes"""
    from pymodaq_gui.resources.material_icons import MaterialIcon
    dockarea = gutils.DockArea()
    app = BeamProfilerApp(dockarea)
    actions = [app.get_action(name) for name in ('simulate',)]
    with loaded_extension(BeamProfiler) as (dashboard, extension):
        actions += [extension.get_action(name) for name in ('grab', 'live')]
        for action in actions:
            assert isinstance(action.icon_unchecked, MaterialIcon), action.text()
    dockarea.close()
