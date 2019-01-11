Example Tango Project
=====================

This project demonstrates how to structure an SKA project that provides a simple 
Tango device coded in PyTango. 

Documentation can be found in the ``docs`` folder.

Notes
-----

1. The ``coverage`` module interferes with PyDev debugging. To work around this 
problem, comment out the pytest ``addopts`` section in setup.cfg.   

1. The tests in ``tests/test_1_test_server_using_devicetestcontext.py``
   execute using the Tango DeviceTestContext helper. These tests create a new 
   device per test, requiring that each DeviceTestContext run in a new process
   to avoid SegmentationFault errors. For more info, see:
   * https://github.com/tango-controls/pytango/pull/77
   * http://www.tango-controls.org/community/forum/c/development/python/testing-tango-devices-using-pytest/?page=1#post-3761
   
   We should form a recommendation on whether a new device should be formed per test or not.

1. Running DeviceTestContext tests _after_ tests using a Tango client results in 
   errors when the DeviceTestContext gets stuck in initialisation. As a workaround, 
   I've set the filenames so that the DeviceTestContext tests run first.
   
   We should form a recommendation on what tests are expected: should projects
   just contain unit tests using DeviceTestContext, or should they also contain
   integration tests using Tango client? When unit testing using DeviceTestContext, 
   how should other devices be mocked?
