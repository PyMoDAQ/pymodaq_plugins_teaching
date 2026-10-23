"""Tests of the scanner and of the exporter registered in the factories"""
from unittest.mock import MagicMock

import numpy as np
import pytest

from pymodaq.utils.scanner.scan_factory import ScannerFactory
from pymodaq_data.h5modules.exporter import ExporterFactory
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_teaching.scanners.scan_1d_fixed import Scan1DFixed, FIXED_POSITIONS
from pymodaq_plugins_teaching.exporters.h5_columns_exporter import H5ColumnsExporter


def make_scanner() -> Scan1DFixed:
    actuator = MagicMock()
    actuator.title = 'Wavelength'
    actuator.units = 'nm'
    settings = Parameter.create(name='scan_settings', type='group', children=[
        {'title': 'Units', 'name': 'units_handling', 'type': 'group', 'children': [
            {'title': 'Display units:', 'name': 'display_units', 'type': 'bool', 'value': False}]}])
    return Scan1DFixed(actuators=[actuator], settings=settings)


def test_scanner_is_registered():
    assert ScannerFactory.get_builder('Scan1D', 'Fixed') is Scan1DFixed


def test_scanner_positions(qapp):
    scanner = make_scanner()
    scanner.set_scan()
    assert np.squeeze(scanner.positions) == pytest.approx(FIXED_POSITIONS)
    assert scanner.n_steps == len(FIXED_POSITIONS)
    assert scanner.get_scan_shape() == (len(FIXED_POSITIONS),)
    assert scanner.evaluate_steps() == len(FIXED_POSITIONS)


class FakeNode:
    """What an exporter needs from an h5 node"""
    name = 'data'
    attrs = {'CLASS': 'CARRAY'}

    def __init__(self, data):
        self._data = data

    def read(self):
        return self._data


def test_exporter_is_registered():
    exporter = ExporterFactory.create_exporter('dat', 'Data in columns')
    assert isinstance(exporter, H5ColumnsExporter)


def test_exporter_writes_columns(tmp_path):
    filename = tmp_path / 'out.dat'
    H5ColumnsExporter().export_data(FakeNode(np.array([[1., 2., 3.], [4., 5., 6.]])), str(filename))
    written = np.loadtxt(filename, delimiter='\t')
    assert written.shape == (3, 2)
    assert written[:, 1] == pytest.approx([4., 5., 6.])
