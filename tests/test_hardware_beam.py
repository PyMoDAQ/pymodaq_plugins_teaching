"""Tests of the simulated beam of hardware/beam.py"""
import numpy as np
import pytest

from pymodaq_plugins_teaching.hardware.beam import gaussian_beam_image


def second_moment_diameters(image):
    """Position and 4 sigma diameters along x and y of an unrotated image, computed with numpy"""
    ny, nx = image.shape
    x, y = np.arange(nx), np.arange(ny)
    px, py = image.sum(axis=0), image.sum(axis=1)
    x0, y0 = (px * x).sum() / px.sum(), (py * y).sum() / py.sum()
    dx = 4 * np.sqrt((px * (x - x0) ** 2).sum() / px.sum())
    dy = 4 * np.sqrt((py * (y - y0) ** 2).sum() / py.sum())
    return x0, y0, dx, dy


def test_shape_and_center():
    image = gaussian_beam_image(shape=(120, 200), center=(80., 40.), size=(30., 20.))
    assert image.shape == (120, 200)
    assert np.unravel_index(np.argmax(image), image.shape) == (40, 80)


def test_sizes_are_the_1_over_e2_diameters():
    image = gaussian_beam_image(center=(150., 100.), size=(60., 30.))
    x0, y0, dx, dy = second_moment_diameters(image)
    assert (x0, y0) == (pytest.approx(150., abs=0.1), pytest.approx(100., abs=0.1))
    assert dx == pytest.approx(60., rel=0.02)
    assert dy == pytest.approx(30., rel=0.02)


def test_noise_is_added():
    clean = gaussian_beam_image(noise=0.)
    noisy = gaussian_beam_image(noise=5.)
    assert not np.allclose(clean, noisy)
