"""Tests of the referencing of the Spectrometer wrapper (no plugin, no GUI)"""
from time import sleep

import pytest

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer, NotReferencedError


def test_referenced_at_once_by_default():
    spectrometer = Spectrometer()
    spectrometer.set_wavelength(500.)
    spectrometer.find_reference()
    assert spectrometer.is_referenced
    assert spectrometer.get_wavelength() == spectrometer.reference_wavelength


def test_wavelength_is_not_available_while_referencing():
    spectrometer = Spectrometer()
    spectrometer.needs_referencing = True
    spectrometer.find_reference()
    assert not spectrometer.is_referenced
    for call in (spectrometer.get_wavelength, spectrometer.get_wavelength_axis, spectrometer.grab_spectrum,
                 lambda: spectrometer.set_wavelength(500.)):
        with pytest.raises(NotReferencedError):
            call()


def test_wavelength_is_available_after_referencing():
    spectrometer = Spectrometer()
    spectrometer.needs_referencing = True
    spectrometer.homing_time = 0.05
    spectrometer.find_reference()
    sleep(0.1)
    assert spectrometer.is_referenced
    assert spectrometer.get_wavelength() == spectrometer.reference_wavelength
