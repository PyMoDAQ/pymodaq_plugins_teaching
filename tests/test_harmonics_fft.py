"""Tests of the harmonics + Fourier transform example: plugin by inheritance, app, DataMixer model"""
import numpy as np
import pytest

from pymodaq.utils.plugin_testing import make_detector, grab_and_wait
from pymodaq_data.data import DataRaw, DataToExport, Axis

from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_1D.daq_1Dviewer_HarmonicsFT import \
    DAQ_1DViewer_HarmonicsFT
from pymodaq_plugins_teaching.app.harmonics_fft_app import HarmonicsFFTApp, fft_numpy, fft_pymodaq
from pymodaq_plugins_teaching.models.fft_model import DataMixerModelFFT
from pymodaq.extensions.data_mixer.models.equation_model import DataMixerModelEquation
from pymodaq_gui import utils as gutils


def sine(freq=5., npts=512):
    t = np.linspace(0, 1, npts, endpoint=False)
    return DataRaw('sine', data=[np.sin(2 * np.pi * freq * t)], dim='Data1D',
                   axes=[Axis('time', 's', data=t)])


def test_numpy_and_pymodaq_find_the_same_frequency():
    dwa = sine(5.)
    dwa_np, dwa_pmq = fft_numpy(dwa), fft_pymodaq(dwa)
    f_np = dwa_np.get_axis_from_index(0)[0].get_data()[np.argmax(dwa_np[0])]
    omega = dwa_pmq.get_axis_from_index(0)[0].get_data()
    omega_pmq = abs(omega[np.argmax(dwa_pmq[0])])
    assert f_np == pytest.approx(5., abs=0.5)
    assert omega_pmq == pytest.approx(2 * np.pi * f_np, rel=0.15)


def test_plugin_sends_the_fft(qapp):
    det = make_detector(DAQ_1DViewer_HarmonicsFT)
    assert det.initialized
    dte = grab_and_wait(det)
    assert {'Harmonics', 'HarmonicsFT'} <= set(dte.get_names())


def test_model_computes_the_fft():
    dte = DataToExport('det', data=[sine(5.)])
    model = DataMixerModelFFT.__new__(DataMixerModelFFT)
    out = model.process_dte(dte)
    assert out.get_names() == ['FFT_sine']


def test_equation_model_gives_the_same_result():
    """No code needed: the equation model of the DataMixer does the same with a formula"""
    dte = DataToExport('det', data=[sine(5.)])
    model = DataMixerModelEquation.__new__(DataMixerModelEquation)
    result = model.compute_formula('{det/sine}.ft().abs()', dte, name='fft')
    np.testing.assert_allclose(result[0], fft_pymodaq(dte[0])[0])


@pytest.mark.parametrize('method', ['numpy', 'pymodaq'])
def test_app(qtbot, method):
    dockarea = gutils.DockArea()
    app = HarmonicsFFTApp(dockarea)
    app.settings.child('method').setValue(method)
    app.grab()
