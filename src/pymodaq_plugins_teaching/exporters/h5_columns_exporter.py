"""A minimal exporter of h5 nodes: the data of an array node written in a text file, in columns

An exporter is a class registered in the ExporterFactory. Once the package is installed (``pip install -e .`` with
``h5exporters = true`` in pyproject.toml), the format is listed by *Export as* of the H5Browser.
"""
import numpy as np

from pymodaq_data.h5modules.backends import Node
from pymodaq_data.h5modules.exporter import ExporterFactory, H5Exporter


@ExporterFactory.register_exporter()
class H5ColumnsExporter(H5Exporter):
    """Export an array node as a text file, one column per row of 2D data"""

    FORMAT_DESCRIPTION = "Data in columns"  # displayed in the file filters
    FORMAT_EXTENSION = "dat"  # extension of the exported file

    def export_data(self, node: Node, filename: str) -> None:
        if 'ARRAY' not in node.attrs['CLASS']:
            raise ValueError(f'{node.name} is not an array node, only the array nodes can be exported')
        data = np.atleast_2d(np.asarray(node.read(), dtype=float))
        if data.shape[0] < data.shape[1]:  # one row per data set: write one column per data set
            data = data.T
        np.savetxt(filename, data, fmt='%.6e', delimiter='\t')
