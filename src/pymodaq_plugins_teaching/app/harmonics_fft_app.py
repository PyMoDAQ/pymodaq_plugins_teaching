"""Harmonics generator and its Fourier transform, computed in two ways

The generator is the Harmonics hardware of pymodaq_plugins_mockexamples (reused, not rewritten). The spectrum is
transformed either directly with numpy or with the methods of the PyMoDAQ data objects, so that the two approaches
can be compared on the same signal.
"""
import numpy as np
from qtpy import QtWidgets

from pymodaq_gui import utils as gutils
from pymodaq_gui.plotting.data_viewers.viewer1D import Viewer1D
from pymodaq_data.data import DataRaw, Axis

from pymodaq_plugins_mockexamples.hardware.harmonics import Harmonics

METHODS = ['numpy', 'pymodaq']


def fft_numpy(dwa: DataRaw) -> DataRaw:
    """Modulus of the FFT with numpy, versus the frequency in 1 / axis units"""
    axis = dwa.get_axis_from_index(0)[0]
    step = float(np.mean(np.diff(axis.get_data())))
    freq = np.fft.rfftfreq(len(axis), d=step)
    modulus = np.abs(np.fft.rfft(dwa[0]))
    return DataRaw('FFT numpy', data=[modulus], dim='Data1D', labels=['|FFT|'],
                   axes=[Axis('Frequency', f'1/({axis.units})', data=freq)])


def fft_pymodaq(dwa: DataRaw) -> DataRaw:
    """Modulus of the FFT with the data object: the new axis (rad / axis units) is computed with it"""
    dwa_ft = dwa.ft().abs()
    dwa_ft.name = 'FFT pymodaq'
    return dwa_ft


class HarmonicsFFTApp(gutils.CustomApp):

    params = [
        {'title': 'Method:', 'name': 'method', 'type': 'list', 'limits': METHODS, 'value': METHODS[0]},
        {'title': 'N harmonics:', 'name': 'n_harmonics', 'type': 'int', 'value': 3, 'min': 1},
        {'title': 'Omega noise (eV):', 'name': 'omega_noise', 'type': 'float', 'value': 0., 'min': 0.},
    ]

    def __init__(self, parent: gutils.DockArea):
        super().__init__(parent)
        self.generator = Harmonics()
        self.setup_ui()

    def setup_docks_and_widgets(self):
        self.docks['settings'] = gutils.Dock('Settings')
        self.dockarea.addDock(self.docks['settings'])
        self.docks['settings'].addWidget(self.settings_tree)

        self.docks['signal'] = gutils.Dock('Spectrum')
        self.dockarea.addDock(self.docks['signal'], 'right', self.docks['settings'])
        self.viewer_signal = Viewer1D(QtWidgets.QWidget())
        self.docks['signal'].addWidget(self.viewer_signal.parent)

        self.docks['fft'] = gutils.Dock('Fourier transform')
        self.dockarea.addDock(self.docks['fft'], 'bottom', self.docks['signal'])
        self.viewer_fft = Viewer1D(QtWidgets.QWidget())
        self.docks['fft'].addWidget(self.viewer_fft.parent)

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        pass

    def setup_actions(self):
        self.add_action('grab', 'Grab', 'camera', 'Generate a spectrum and compute its Fourier transform')

    def connect_things(self):
        self.connect_action('grab', self.grab)

    def grab(self):
        self.generator.n_harmonics = self.settings['n_harmonics']
        self.generator.omega_noise = self.settings['omega_noise']
        spectrum = self.generator.get_spectrum()
        axis = self.generator.get_axis()
        dwa = DataRaw('Harmonics', data=[spectrum.magnitude], dim='Data1D', labels=['Spectrum'],
                      axes=[Axis('Energy', str(axis.units), data=axis.magnitude)])
        self.show_data(dwa)

    def show_data(self, dwa: DataRaw):
        self.viewer_signal.show_data(dwa)
        compute = fft_numpy if self.settings['method'] == 'numpy' else fft_pymodaq
        self.viewer_fft.show_data(compute(dwa))

    def value_changed(self, param):
        self.grab()


def main():
    from pymodaq_gui.qt_utils import mkQApp
    app = mkQApp('Harmonics FFT')

    mainwindow = QtWidgets.QMainWindow()
    dockarea = gutils.DockArea()
    mainwindow.setCentralWidget(dockarea)
    HarmonicsFFTApp(dockarea)
    mainwindow.show()
    app.exec()


if __name__ == '__main__':
    main()
