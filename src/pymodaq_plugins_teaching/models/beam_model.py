import numpy as np

from pymodaq.extensions.data_mixer.model import DataMixerModel

from pymodaq_data.data import DataToExport, DataCalculated
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_teaching.hardware.beam import beam_properties


class DataMixerModelBeam(DataMixerModel):
    """ Position and size of the beam on every 2D data (camera) of the detectors

    The same calculation as the `DAQ_2DViewer_BeamProfiler` plugin, but for any camera of the Dashboard, without
    changing a plugin. The result is a virtual detector that can be used in the DAQ_Scan extension.
    """
    params = []

    def ini_model(self):
        pass

    def update_settings(self, param: Parameter):
        pass

    def process_dte(self, dte: DataToExport) -> DataToExport:
        dte_processed = DataToExport('BeamProperties')
        for dwa in dte.get_data_from_dim('Data2D'):
            x, y, d_major, d_minor, _ = beam_properties(dwa.data[0])
            dte_processed.append(DataCalculated(f'BeamXY_{dwa.name}', data=[np.atleast_1d(x), np.atleast_1d(y)],
                                                labels=['X', 'Y']))
            dte_processed.append(DataCalculated(f'BeamSize_{dwa.name}',
                                                data=[np.atleast_1d(d_major), np.atleast_1d(d_minor)],
                                                labels=['Dmajor', 'Dminor']))
        return dte_processed
