SKA Skeleton Project
====================

This pull request builds on the work for ST3, replacing the plain Python
example app with an example Tango device. 

The build targets defined in ST3 apply to the ST59 branch too. The most
important make targets for this story are 'make build', 'make interactive',
and 'make test', which build an image, start an interactive developer session,
and run the unit tests respectively.

The 'make test' target builds a new application image and launches the example
device in a Tango environment. The tests themselves make Tango calls to the
example device via the network.
