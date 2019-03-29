.. skeleton documentation master file, created by
   sphinx-quickstart on Thu May 17 15:17:35 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. HOME SECTION ==================================================

.. Hidden toctree to manage the sidebar navigation.

.. toctree::
  :maxdepth: 1
  :caption: Home
  :hidden:


.. COMMUNITY SECTION ==================================================

.. Hidden toctree to manage the sidebar navigation.

.. toctree::
  :maxdepth: 1
  :caption: Package-name
  :hidden:

  package/guide

=============
tango-example
=============

Project description
===================

This project is an example of how a Tango device coded in Python can be
structured as an SKA project and integrated with the continuous integration
server. The tango-example project builds upon the `ska_python_skeleton
<https://github.com/ska-telescope/ska_python_skeleton>`_ example project, replacing
the pure Python application in ska_python_skeleton with the 'power supply' Tango
device presented as an example in the PyTango `online documentation
<https://pytango.readthedocs.io/en/stable/server_api/server.html>`_. The
project uses the
`SKA Docker images <https://github.com/ska-telescope/ska-docker>`_, and
shows how source code located in a local workspace can be integrated with
these images.

Quickstart
==========
This project is structured to use Docker containers for development and
testing so that the build environment, test environment and test results are
all completely reproducible and are independent of host environment. It uses
``make`` to provide a consistent UI (see `Makefile targets`_).

Build a new Docker image for the example power supply device with:

::

  make build

Test the device using:

::

  make test

Launch an interactive shell inside a container, with your workspace visible
inside the container:

::

  make interactive

Adapting this project
=====================
This example project can be used as a starting point for a new project. The
general workflow after forking/cloning is to:

#. modify the name of the Docker image so that it refers to your new project
   by editing Makefile and .release (see `Docker tag management`_);
#. if required, modify docker-compose.yml to specify which other Tango devices
   and Docker containers should be available in the test/interactive
   environment for your project (see
   `Test environment / interactive environment`_);
#. add any new build and/or test dependencies by editing Pipfile,
   refreshing Pipfile.lock afterwards (see
   `Python packaging and dependency management`_);
#. introduce new source code and unit tests (see `Device development`_ and
   `Unit tests`_);
#. modify setuptools configuration so 'python setup.py build' build your
   new device (see `Python packaging and dependency management`_);
#. if required, fix up the test-harness directory by adding any required test
   data and/or customising the test Makefile (see `Unit tests`_);
#. Run tests;
#. Commit.

Docker tag management
---------------------
The name/tag of the Docker image created for the project is defined in the
project Makefile. In this example project, the images are tagged as
ska-registry.av.it.pt/tango-example/powersupply:latest. This tag
should be changed to refer to your device.

#. Modify Makefile, changing ``DOCKER_REGISTRY_USER`` and ``PROJECT`` to give
   an appropriate Docker image name for your project.
#. edit .release, modifying the 'release' definition to match the name of your
   project.

The Docker image that results contains a Python environment with all project
dependencies installed, plus a copy of the project source code and unit tests.
The Python environment is located at /venv in the image, while the project source
code is located in the /app folder.

Test environment / interactive environment
------------------------------------------
The docker-compose.yml file for each project defines which Docker containers
should be created when starting an interactive development session or a test
session. Note that the interactive session and tests do not execute in any of
the containers defined in docker-compose.yml, but in an separate container
created alongside those defined in the file.

In this example project, docker-compose.yml defines a test environment
comprising three containers: a Tango database; a databaseds server, and a
container for the example power supply device. This project illustrates two
execution scenarios for unit tests: one, where unit tests and device server
run in the same container, and a second scenario where unit tests and the
device server execute in separate containers. The power supply device
specified in docker-compose.yml allow this second scenario.

The docker-compose.yml file should be customised for your project. Note that
the same container definitions are used for 'make test' and 'make interactive'.

(Optional) Docker entry point management:

#. Modify Dockerfile, redefining CMD to give the name of the Python file
   that should be executed if the Docker image is run without arguments.

Python packaging and dependency management
-------------------------------------------
Just as for the ska_python_skeleton project, Python runtime dependencies and test
dependencies for the device are defined in the project Pipfile. For the
example Tango device in this project, the dependencies are pytango, plus
pytango's dependency: numpy. The versions are pinned to use the same version
of pytango and numpy contained in the ska-python-builder Docker image, which
allows the cached versions of pytango and numpy to be reused, thus saving
time when the image is rebuilt.

The steps to modify the project dependencies as required for your project are:

#. edit the project dependencies for your device (pytango, numpy, etc.) in the
   Pipfile;
#. whenever Pipfile is edited, execute ``make build && make piplock`` to
   generate an updated Pipfile.lock inside a container and copy it into your
   local workspace;
#. update the project dependencies in setup.py to match those in the Pipfile.

The Python packages and modules provided by the project are defined in
setup.cfg and setup.py. For this example project, these files refer to the
PowerSupply device contained in the powersupply package. These references
should be modified as required for your project:

#. update setup.py to refer to your project, updating references to
   'powersupply' (the package for the example device provided in this example
   project) to point to the package(s) for your device;
#. modify setup.cfg, replacing any references to powersupply with references
   to the Python package(s) for your device.

Device development
------------------
The code for your device exists on disk in your local filesystem and can be
edited with the text editor or IDE of your choice. Changes made locally are
seen immediately in the Docker container when using ``make interactive`` (see
section on `Makefile targets`_), or on the next image rebuild when an
interactive session is not used.

The source code for the power supply device in this example project can be
found in the /powersupply directory. SKA convention is that device classes
should be contained in a Python module contained in a Python package. In
this project, the power supply device is defined in the powersupply.py module
contained in the powersupply package. When adding your device, it should be
structured similarly.

Unit tests
----------
Source code for the power supply device's unit tests can be found in the
/tests folder. In this example project, tests are not executed in the native
host. Instead, the device source code is prepared into a Docker image, a
container is launched using this image, and the tests run inside this
container.

Files in the 'test-harness' directory are made available to the container
during the test procedure. Files in this direcotry are not permanently
included in the Docker image. Hence, the 'test-harness' directory includes
files that are required for unit testing (data files, makefiles, etc.) that
are not required / should not be included for production. The test-harness
directory in the example project includes a Makefile; the Makefile defines a
``test`` make target, which is launched inside a container at runtime and
defines the entry point for the test procedure for the device. This ``make
test`` target can also be executed inside a container during a ``make
interactive`` session. For a Python project such as this, the 'test' target
calls the standard 'python setup.py test' procedure. The 'test' target for
non-Python projects will call different procedures.

test-harness/Makefile should be customised for your project. If testing using
a tango client, the 'tango_admin' line should be modified to wait for your
device to become available rather than the example device. If your tests
do not use a tango client, the 'tango_admin' line can be deleted.

Makefile targets
================
This project contains a Makefile which acts as a UI for building Docker
images, testing images, and for launching interactive developer environments.
The following make targets are defined:

+-----------------+------------------------------------------------+
| Makefile target | Description                                    |
+=================+================================================+
| build           | Build a new application image                  |
+-----------------+------------------------------------------------+
| test            | Test the application image                     |
+-----------------+------------------------------------------------+
| interactive     | Launch a minimal Tango system (including the   |
|                 | device under development), mounting the source |
|                 | directory from the host machine inside the     |
|                 | container                                      |
+-----------------+------------------------------------------------+
| piplock         | Overwrite the Pipfile.lock in the source       |
|                 | with the generated version from the            |
|                 | application image                              |
+-----------------+------------------------------------------------+
| push            | Push the application image to the Docker       |
|                 | registry                                       |
+-----------------+------------------------------------------------+
| up              | launch the development/test container service  |
|                 | on which this application depends              |
+-----------------+------------------------------------------------+
| down            | stop all containers launched by 'make up' and  |
|                 | 'make interactive'                             |
+-----------------+------------------------------------------------+
| help            | show a summary of the makefile targets above   |
+-----------------+------------------------------------------------+

Creating a new application image
--------------------------------
``make build`` target creates a new Docker image for the application based
on the 'ska-python-runtime' image. To optimise final image size and to support
the inclusion of C extension Python libraries such as pytango, the application
is built inside an intermediate Docker image which includes compilers and
cached eggs and wheels for commonly-used Python libraries
('ska-python-builder'). The resulting Python environment from this
intermediate stage is copied into a final image which extends a minimal SKA
Python runtime environment ('ska-python-runtime'), to give the final Docker
image for this application.

Interactive development using containers
----------------------------------------
``make interactive`` launches an interactive session using the application
image, mounting the project source directory at /app inside the container.
This allows the container to run code from the local workspace. Any changes
made to the project source code will immediately be seen inside the container.

Test execution
--------------
``make test`` runs the application test procedure defined in
test-harness/Makefile in a temporary container. The Makefile example for
this project runs 'python setup.py test' and copies the resulting output and
test artefacts out of the container and into a 'build' directory, ready for
inclusion in the CI server's downloadable artefacts.
