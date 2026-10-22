"""Tests of the beam profiler of the module B: analysis function, 2D plugin, standalone app and Dashboard extension"""
import numpy as np
import pytest

from pymodaq.utils.plugin_testing import make_detector, grab_and_wait, loaded_extension, PluginExtensionChecks
from pymodaq_data.data import DataRaw, DataToExport, Axis
from pymodaq_gui import utils as gutils

from pymodaq_plugins_teaching.beam import beam_properties, gaussian_beam_image
from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BeamProfiler import \
    DAQ_2DViewer_BeamProfiler
from pymodaq_plugins_teaching.extensions.beam_profiler import BeamProfiler
from pymodaq_plugins_teaching.app.beam_profiler_app import BeamProfilerApp


class TestExtensionsLoad(PluginExtensionChecks):
    """One loading test per extension of the package (provided by PyMoDAQ)"""
    strict_imports = True


class TestAnalysis:
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
