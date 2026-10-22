PyMoDAQ Plugins Teaching
########################

.. image:: https://img.shields.io/pypi/v/pymodaq_plugins_teaching.svg
   :target: https://pypi.org/project/pymodaq_plugins_teaching/
   :alt: Latest Version

.. image:: https://readthedocs.org/projects/pymodaq/badge/?version=latest
   :target: https://pymodaq.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_teaching/workflows/Upload%20Python%20Package/badge.svg
    :target: https://github.com/PyMoDAQ/pymodaq_plugins_teaching

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_teaching/actions/workflows/Test.yml/badge.svg
    :target: https://github.com/PyMoDAQ/pymodaq_plugins_teaching/actions/workflows/Test.yml


PyMoDAQ plugins developed specifically to teach how to create new plugins


Branches
========

* ``main``: the skeleton of ``pymodaq_plugins_template`` (plugins to complete) and the wrappers of the ``hardware`` folder
  that the trainees use. This is the starting point of the exercises.
* ``correction-module-a``: the solution of the module A (``DAQ_Move_Monochromator``,
  ``DAQ_0DViewer_PhotodiodeMonochromator``, ``DAQ_1DViewer_Spectrometer``).
* ``correction-module-b``: the solution of the modules A and B (adds the beam profiler plugin, app and extension).

Authors
=======

* Sebastien J. Weber

Instruments
===========
Below is the list of instruments included in this plugin

Actuators
+++++++++

* **Monochromator**: central wavelength of the simulated monochromator of the teaching spectrometer



Viewer0D
++++++++

* **PhotodiodeMonochromator**: intensity of the simulated spectrum at the central wavelength of the monochromator


Viewer1D
++++++++

* **Spectrometer**: simulated spectrum on the wavelength axis of the monochromator (master/slave with the actuator)


Viewer2D
++++++++

ViewerND
++++++++
