from pymodaq.extensions.data_mixer.model import DataMixerModel

from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter


class DataMixerModelFFT(DataMixerModel):
    """ Modulus of the Fourier transform of every 1D data of the detectors

    The same result is obtained without any code with the equation model of the DataMixer and the formula
    `{Harmonics/Harmonics}.ft().abs()` (full name of the data between curly brackets).
    """
    params = []

    def ini_model(self):
        pass

    def update_settings(self, param: Parameter):
        pass

    def process_dte(self, dte: DataToExport) -> DataToExport:
        dte_processed = DataToExport('FFT')
        for dwa in dte.get_data_from_dim('Data1D'):
            dwa_ft = dwa.ft().abs()
            dwa_ft.name = f'FFT_{dwa.name}'
            dte_processed.append(dwa_ft)
        return dte_processed
