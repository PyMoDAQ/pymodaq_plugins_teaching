"""Beam profiler as a standalone application: no instrument, the beam is simulated

This is the first step of the module B: how a `CustomApp` is built (docks, settings, actions, slots). The same
analysis, driven by a camera of the Dashboard, is the `BeamProfiler` extension.
"""
import numpy as np
from qtpy import QtWidgets

from pymodaq_gui import utils as gutils
from pymodaq_gui.plotting.data_viewers.viewer2D import Viewer2D
from pymodaq_gui.utils.widgets.lcd import LCD
from pymodaq_data.data import DataRaw, Axis

from pymodaq_plugins_teaching.beam import beam_properties, gaussian_beam_image


class BeamProfilerApp(gutils.CustomApp):

    params = [
        {'title': 'Beam size X:', 'name': 'size_x', 'type': 'float', 'value': 40., 'min': 4.},
        {'title': 'Beam size Y:', 'name': 'size_y', 'type': 'float', 'value': 20., 'min': 4.},
        {'title': 'Angle (deg):', 'name': 'angle', 'type': 'float', 'value': 0.},
        {'title': 'Noise:', 'name': 'noise', 'type': 'float', 'value': 5., 'min': 0.},
    ]

    def __init__(self, parent: gutils.DockArea):
        super().__init__(parent)
        self.setup_ui()

    def setup_docks_and_widgets(self):
        self.docks['settings'] = gutils.Dock('Settings')
        self.dockarea.addDock(self.docks['settings'])
        self.docks['settings'].addWidget(self.settings_tree)

        self.docks['viewer2D'] = gutils.Dock('Image')
        self.dockarea.addDock(self.docks['viewer2D'], 'right', self.docks['settings'])
        self.viewer = Viewer2D(QtWidgets.QWidget())
        self.docks['viewer2D'].addWidget(self.viewer.parent)

        self.docks['lcds'] = gutils.Dock('Beam properties')
        self.dockarea.addDock(self.docks['lcds'], 'bottom', self.docks['settings'])
        self.lcd = LCD(QtWidgets.QWidget(), Nvals=5, labels=['X', 'Y', 'dmajor', 'dminor', 'theta'])
        self.docks['lcds'].addWidget(self.lcd.parent)

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        pass

    def setup_actions(self):
        self.add_action('simulate', 'Simulate', 'camera', 'Simulate a beam image and analyse it')

    def connect_things(self):
        self.connect_action('simulate', self.simulate)

    def simulate(self):
        """Simulate an image of the beam with the settings, show it and analyse it"""
        image = gaussian_beam_image(size=(self.settings['size_x'], self.settings['size_y']),
                                    angle=self.settings['angle'], noise=self.settings['noise'])
        self.show_data(image)

    def show_data(self, image: np.ndarray):
        dwa = DataRaw('beam', data=[image], dim='Data2D',
                      axes=[Axis('y', 'pixel', data=np.arange(image.shape[0]), index=0),
                            Axis('x', 'pixel', data=np.arange(image.shape[1]), index=1)])
        self.viewer.show_data(dwa)
        x, y, d_major, d_minor, phi = beam_properties(image)
        self.lcd.setvalues([np.array([val]) for val in (x, y, d_major, d_minor, np.rad2deg(phi))])

    def value_changed(self, param):
        self.simulate()


def main():
    from pymodaq_gui.qt_utils import mkQApp
    app = mkQApp('Beam profiler')

    mainwindow = QtWidgets.QMainWindow()
    dockarea = gutils.DockArea()
    mainwindow.setCentralWidget(dockarea)
    BeamProfilerApp(dockarea)
    mainwindow.show()
    app.exec()


if __name__ == '__main__':
    main()
