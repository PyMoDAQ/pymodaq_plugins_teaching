"""Beam profiler as a Dashboard extension

Any 2D detector (camera) of the Dashboard experiment can be used: the extension gets its images through the
`modules_manager`, computes the position and size of the beam and displays them.
"""
import numpy as np
from qtpy import QtWidgets, QtCore

from pymodaq_gui import utils as gutils
from pymodaq_gui.plotting.data_viewers.viewer2D import Viewer2D
from pymodaq_gui.utils.widgets.lcd import LCD
from pymodaq_utils.logger import set_logger, get_module_name
from pymodaq_data.data import DataToExport
from pymodaq.utils.custom_ext import CustomExt

from pymodaq_plugins_teaching.beam import beam_properties

logger = set_logger(get_module_name(__file__))

EXTENSION_NAME = 'Beam Profiler'  # the name displayed in the extension list of the Dashboard
CLASS_NAME = 'BeamProfiler'  # the name of the class defined below


class BeamProfiler(CustomExt):

    params = [
        {'title': 'Camera:', 'name': 'camera', 'type': 'list', 'limits': [], 'tip': 'Any 2D detector of the experiment'},
        {'title': 'Live refresh (ms):', 'name': 'refresh', 'type': 'int', 'value': 200, 'min': 20},
    ]

    def __init__(self, parent: gutils.DockArea, dashboard):
        super().__init__(parent, dashboard, add_toolbar_break=False)
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.grab)
        self.setup_ui()

    def setup_docks_and_widgets(self):
        self.docks['settings'] = gutils.Dock('Settings')
        self.dockarea.addDock(self.docks['settings'])
        self.docks['settings'].addWidget(self.settings_tree)

        self.docks['viewer2D'] = gutils.Dock('Camera data')
        self.dockarea.addDock(self.docks['viewer2D'], 'right', self.docks['settings'])
        self.target_viewer = Viewer2D(QtWidgets.QWidget())
        self.docks['viewer2D'].addWidget(self.target_viewer.parent)

        self.docks['lcds'] = gutils.Dock('Beam properties')
        self.dockarea.addDock(self.docks['lcds'], 'bottom', self.docks['settings'])
        self.lcd = LCD(QtWidgets.QWidget(), Nvals=5, labels=['X', 'Y', 'dmajor', 'dminor', 'theta'])
        self.docks['lcds'].addWidget(self.lcd.parent)

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        self.create_dashboard_toolbar(add_break=False)

    def setup_actions(self):
        self.add_action('grab', 'Grab', 'camera', 'Grab one image from the camera and analyse it')
        self.add_action('live', 'Live', 'run2', 'Grab and analyse continuously', checkable=True)

    def connect_things(self):
        self.connect_action('grab', self.grab)
        self.connect_action('live', self.set_live)

    def do_things_after_experiment_set(self, experiment_name: str, show_dashboard: bool = None):
        """The instruments of the Dashboard changed: refresh the list of cameras (the base class updates the
        `modules_manager` first)"""
        super().do_things_after_experiment_set(experiment_name, show_dashboard)
        self.settings.child('camera').setLimits(self.modules_manager.detectors_name)

    def value_changed(self, param):
        if param.name() == 'camera' and param.value() in self.modules_manager.detectors_name:
            self.modules_manager.selected_detectors_name = [param.value()]

    def grab(self):
        """Ask the selected camera for an image through the modules manager, then analyse it"""
        if not self.modules_manager.selected_detectors_name:
            self.update_status('Select a camera in the settings')
            return
        self.show_data(self.modules_manager.grab_data())

    def set_live(self, do_live: bool):
        if do_live:
            self._timer.start(self.settings['refresh'])
        else:
            self._timer.stop()

    def show_data(self, dte: DataToExport):
        """Display the first raw 2D data of the received data and the properties of the beam"""
        dte_raw = dte.get_data_from_source('raw')  # not the ROIs the user may have defined on the camera viewer
        dwa2D = dte_raw.get_data_from_dim('Data2D')
        if len(dwa2D) == 0:
            self.update_status('No 2D data received')
            return
        dwa = dwa2D[0]
        self.target_viewer.show_data(dwa)
        x, y, d_major, d_minor, phi = beam_properties(dwa.data[0])
        self.lcd.setvalues([np.array([val]) for val in (x, y, d_major, d_minor, np.rad2deg(phi))])

    def _quit_fun(self) -> bool:
        self._timer.stop()
        return True


def main():
    """Run the extension on its own: loads a Dashboard (hidden), then the extension, ``-x EXPERIMENT_NAME`` and
    ``-s STATE_NAME`` select the experiment and the state"""
    import sys
    from pymodaq_gui.qt_utils import mkQApp
    from pymodaq.dashboard import load_dashboard_with_arguments
    from pymodaq.utils.gui_utils.loader_utils import create_extension

    app = mkQApp(EXTENSION_NAME)
    win, dashboard, _ = load_dashboard_with_arguments(show_dashboard=False, load_extension=False)
    win.mainwindow.setVisible(False)
    win_ext, ext = create_extension(dashboard, BeamProfiler, show_extension=True)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
