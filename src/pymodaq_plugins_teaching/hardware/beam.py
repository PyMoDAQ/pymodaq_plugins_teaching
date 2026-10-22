"""Simulation of the image of a laser beam, for the exercises of the module B (the mock camera, the demo app...)

The measurement of the beam (position and size) is what the trainees write, see the correction branches."""
from typing import Tuple

import numpy as np

from pymodaq_utils.math_utils import gauss2D


# gauss1D(x, x0, dx) = exp(-2 ln2 (x - x0)^2 / dx^2) = exp(-2 (x - x0)^2 / w^2) with w = dx / sqrt(ln2) the beam radius at
# 1/e^2: the 1/e^2 diameters D = 2 w used here correspond to dx = D sqrt(ln2) / 2
D_TO_DX = np.sqrt(np.log(2)) / 2


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
    image = amplitude * gauss2D(np.arange(nx), center[0], size[0] * D_TO_DX,
                                np.arange(ny), center[1], size[1] * D_TO_DX, angle=angle)
    if noise > 0:
        image = image + noise * np.random.rand(ny, nx)
    return image
