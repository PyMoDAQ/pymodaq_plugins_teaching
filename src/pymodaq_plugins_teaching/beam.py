"""Small helpers to work with the image of a laser beam, used by the beam profiler plugin, app and extension"""
from typing import Tuple

import numpy as np

import laserbeamsize as lbs


def beam_properties(image: np.ndarray) -> Tuple[float, float, float, float, float]:
    """Compute the position and size of the beam on an image (ISO 11146 second moments)

    Parameters
    ----------
    image: ndarray
        a 2D image of the beam

    Returns
    -------
    x, y: center of the beam (pixels)
    d_major, d_minor: diameters of the beam along its major and minor axes (pixels)
    phi: angle of the major axis (radians)
    """
    x, y, d_major, d_minor, phi = lbs.beam_size(np.asarray(image, dtype=float))
    return float(x), float(y), float(d_major), float(d_minor), float(phi)


def gaussian_beam_image(shape: Tuple[int, int] = (200, 300), center: Tuple[float, float] = (150., 100.),
                        size: Tuple[float, float] = (40., 20.), angle: float = 0., noise: float = 0.,
                        amplitude: float = 1000.) -> np.ndarray:
    """Simulate the image of a gaussian beam, for the demo app and for the tests

    Parameters
    ----------
    shape: (ny, nx) number of pixels of the image
    center: (x0, y0) position of the center (pixels)
    size: (dx, dy) 1/e^2 diameters along the (rotated) x and y axes of the beam (pixels)
    angle: rotation angle of the beam (degrees)
    noise: amplitude of the random noise added to the image
    """
    ny, nx = shape
    x, y = np.meshgrid(np.arange(nx), np.arange(ny))
    theta = np.deg2rad(angle)
    xr = (x - center[0]) * np.cos(theta) + (y - center[1]) * np.sin(theta)
    yr = -(x - center[0]) * np.sin(theta) + (y - center[1]) * np.cos(theta)
    image = amplitude * np.exp(-2 * ((xr / (size[0] / 2)) ** 2 + (yr / (size[1] / 2)) ** 2))
    if noise > 0:
        image = image + noise * np.random.rand(ny, nx)
    return image
