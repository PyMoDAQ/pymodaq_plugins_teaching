"""A 1D scanner with fixed positions: useless but pedagogical

It shows what a scanner is: a class registered in the ScannerFactory that gives DAQ_Scan the list of positions to
visit. Here the positions are written in the code, so that nothing else is in the way of the factory pattern.
Once the package is installed (``pip install -e .`` with ``scanners = true`` in pyproject.toml), the scan type
``Scan1D`` / ``Fixed`` appears in the scan selector of DAQ_Scan.
"""
from typing import List, TYPE_CHECKING

import numpy as np

from pymodaq.utils.scanner.scan_factory import ScannerFactory
from pymodaq.utils.scanner.scanners._1d_scanners import Scan1DBase

if TYPE_CHECKING:
    from pymodaq.control_modules.daq_move import DAQ_Move

FIXED_POSITIONS = [0., 1., 2., 5., 10.]  # in the units of the actuator


@ScannerFactory.register()
class Scan1DFixed(Scan1DBase):
    """Scan an actuator on a fixed list of positions"""

    scan_subtype = 'Fixed'  # with scan_type ('Scan1D', from Scan1DBase), the identifier of the scanner
    params = []  # no setting: the positions are fixed
    n_axes = 1

    def __init__(self, actuators: List['DAQ_Move'] = None, settings=None, **_ignored):
        super().__init__(actuators=actuators, settings=settings)

    def set_scan(self):
        """Computes all the mandatory attributes (positions, n_steps, axes_unique...) from the positions"""
        self.get_info_from_positions(np.array(FIXED_POSITIONS))

    def evaluate_steps(self) -> int:
        """Number of steps, evaluated before the scan is computed (compared with the limit of the configuration)"""
        return len(FIXED_POSITIONS)
