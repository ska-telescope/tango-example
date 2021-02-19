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

=====================
Tango-example project
=====================

This project is an example of how a Tango device coded in Python can be
structured as an SKA project and integrated with the continuous integration
server. The tango-example project builds upon the `ska-python-skeleton
<https://github.com/ska-telescope/ska-python-skeleton>`_ example project, replacing
the pure Python application in ska-python-skeleton with the 'power supply' Tango
device presented as an example in the PyTango `online documentation
<https://pytango.readthedocs.io/en/stable/server_api/server.html>`_. The
project uses the
`SKA Tango images <https://gitlab.com/ska-telescope/ska-tango-images>`_, and
shows how source code located in a local workspace can be integrated with
these images.

Quickstart
==========
This project is structured to use Docker containers for development and
testing so that the build environment, test environment and test results are
all completely reproducible and are independent of host environment. It uses
``make`` to provide a consistent UI (see `Makefile targets`_).

You will need to install `minikube` or equivalent k8s installation in order to set up your test environment.
You can follow the instruction at `here <https://gitlab.com/ska-telescope/sdi/deploy-minikube/>`_

Build a new Docker image for the example power supply device with:

::

  make build

Test the device using:

::
  make install-chart
  make wait
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
#. if required, modify `charts/tango-example` helm chart to specify which other Tango devices
   and Docker containers should be available in the test/interactive
   environment for your project (see
   `Test environment / interactive environment`_);
#. (Optional) Modify the `charts/tango-example/templates` to extend your device and introduce new configuration options that are not available in the existing templates.
#. add any new build and/or test dependencies by editing Pipfile,
   refreshing Pipfile.lock afterwards (see
   `Python packaging and dependency management`_);
#. Modify the `charts/test-umbrella/Charts.yaml` to introduce new dependencies for your test environment if you have any.   
#. introduce new source code and unit tests (see `Device development`_ and
   `Unit tests`_);
#. modify setuptools configuration so 'python setup.py build' build your
   new device (see `Python packaging and dependency management`_);
#. if required, fix up the post-deployment directory by adding any required test
   data and/or customising the test Makefile (see `Unit tests`_);
#. Run tests;
#. Commit.
#. Publish your chart by triggering the manual job. (Optional: Customise publishing according to the
 `guidelines <https://developer.skatelescope.org/en/latest/development/software_package_release_procedure.html#package-and-publish-helm-charts-to-the-ska-helm-chart-repository>`_)

Docker tag management
---------------------
The name/tag of the Docker image created for the project is defined in the
project Makefile. In this example project, the images are tagged as
nexus.engageska-portugal.pt/tango-example/powersupply:latest. This tag
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

This project uses Helm Charts for deploying a development/test environment. All of the related files could be found under `charts/` folder.

 - `charts/tango-example` hart is the main tango-example chart to deploy tango-example in a standalone helm deployment. 
 It defines all the deviceservers it uses in the `Chart.yaml` file and the necessary variables in the `values.yaml` file.
 You can also add your own deviceservers or other definitions using `templates/` folder as a base.
 - `charts/test-umbrella` chart defines the umbrella chart with its dependencies in the `Charts.yaml` file. 
 You can see all the dependencies in the `Charts.yaml` file and new ones for your own devices.

The `charts/tango-example` helm chart defines which pods (a pod contains single device server container)
should be created when starting an interactive development session or a test
session. Note that the interactive session and tests do not execute in any of
the containers defined in the Helm charts, but in an separate container
created alongside those defined in the file.

In this example project, `charts/tango-example` helm chart defines a test environment
comprising three containers: a Tango database; a databaseds server, and an
example power supply device. This project illustrates the 
execution scenarios for unit tests in which unit tests and the
device server execute in separate containers (each in a k8s pod).

The `charts/tango-example` helm chart should be customised for your project. Note that
the same container definitions are used for 'make test' and 'make interactive'.

(Optional) Docker entry point management:

#. Modify Dockerfile, redefining CMD to give the name of the Python file
   that should be executed if the Docker image is run without arguments.

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

Files in the `post-deployment` directory are made available to the container
during the test procedure. Files in this directory are not permanently
included in the Docker image. Hence, the `post-deployment` directory includes
files that are required for unit testing (data files, makefiles, etc.) that
are not required / should not be included for production. The `post-deployment`
directory in the example project includes a Makefile; the Makefile defines a
``test`` make target, which is launched inside a container at runtime and
defines the entry point for the test procedure for the device. This ``make
test`` target can also be executed inside a container during a ``make
interactive`` session. For a Python project such as this, the 'test' target
calls the standard 'python setup.py test' procedure. The 'test' target for
non-Python projects will call different procedures.

`post-deployment`/Makefile should be customised for your project. If testing using
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
| push            | Push the application image to the Docker       |
|                 | registry                                       |
+-----------------+------------------------------------------------+
| install-chart   | launch the development/test container service  |
|                 | on which this application depends              |
+-----------------+------------------------------------------------+
| uninstall-chart | stop all containers launched by                |
|                 | 'make install-chart' and 'make interactive'    |
+-----------------+------------------------------------------------+
| help            | show a summary of the makefile targets above   |
+-----------------+------------------------------------------------+


Json Configuration
------------------
The tool for configure the database is `lib-maxiv-dsconfig <https://github.com/MaxIV-KitsControls/lib-maxiv-dsconfig>`_.
To execute it, please use the docker image at the following link: `tango-dsconfig <https://nexus.engageska-portugal.pt/#browse/search/docker:f898b3903cb99c590fc2d6cb8798051b:a4757bcaa62b6306470e54025c0ba524>`_.
Note that the environment variable DSCONFIG_JSON_FILE use a volume called 'tango-example' to access the project folder.

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
`post-deployment`/Makefile in a temporary k8s deployment. The Makefile example for
this project runs 'python setup.py test' and copies the resulting output and
test artefacts out of the container and into a 'build' directory, ready for
inclusion in the CI server's downloadable artefacts.


Kubernetes integration
======================

The Tango Example has been enhanced to include an example of deploying the application suite on Kubernetes.  This has been done as a working example of the `Orchestration Guidelines <http://developer.skatelescope.org/en/latest/development/orchestration-guidelines.html>`_.  Included is a `Helm Chart <https://helm.sh/docs/>`_ and a set of ``Makefile`` directives that encapsulate the process of deploying and testing the powersupply example on a target cluster.


Extended Makefile targets
-------------------------
There are an extended set of make targets are defined that cover Kubernetes based testing and deployment:

+-----------------+------------------------------------------------+
| Makefile target | Description                                    |
+=================+================================================+
| delete_namespace| delete the kubernetes namespace                |
+-----------------+------------------------------------------------+
| describe        | describe Pods executed from Helm chart         |
+-----------------+------------------------------------------------+
| k8s             | Which kubernetes are we connected to           |
+-----------------+------------------------------------------------+
| kubeconfig      | export current KUBECONFIG as base64 ready for  |
|                 | KUBE_CONFIG_BASE64                             |
+-----------------+------------------------------------------------+
| lint            | lint check the helm chart                      |
+-----------------+------------------------------------------------+
| logs            | show Helm chart POD logs                       |
+-----------------+------------------------------------------------+
| namespace       | create the kubernetes namespace                |
+-----------------+------------------------------------------------+
| rk8s_test       | run k8s_test on K8s using gitlab-runner        |
+-----------------+------------------------------------------------+
| rlint           | run lint check on Helm Chart with gitlab-runner|
+-----------------+------------------------------------------------+
| show            | show the helm chart                            |
+-----------------+------------------------------------------------+


Test execution on Kubernetes
----------------------------

The test execution has been configured to run by default on `Minikube <https://github.com/kubernetes/minikube>`_ so that testing can be carried out locally.  For remote execution, further configuration would be required to handle `PersistentVolume <https://kubernetes.io/docs/concepts/storage/persistent-volumes/>`_ storage correctly.

The Deployment framework is based on Helm 3.

Setting variables
~~~~~~~~~~~~~~~~~

Variables can be set to influence the deployment, and should be placed in a ``PrivateRules.mak`` file in the root of the project directory.  Variables in this file and imported to override ``Makefile`` defaults:


+-------------------+--------------------+------------------------------------------------+
| Makefile variable | Default            | Description                                    |
+===================+====================+================================================+
| KUBE_NAMESPACE    | default            | the Kubernetes Namespace for deployment        |
+-------------------+--------------------+------------------------------------------------+
| UMBRELLA_CHART_PATH  | test-umbrella   | the Helm chart name for deployment             |
+-------------------+--------------------+------------------------------------------------+
| RELEASE_NAME      | test               | the Helm release name for deployment           |
+-------------------+--------------------+------------------------------------------------+
| KUBECONFIG        | /etc/deploy/config | KUBECONFIG location for ``kubectl``            |
+-------------------+--------------------+------------------------------------------------+
| KUBE_CONFIG_BASE64| <empty>            | base64 encoded contents of KUBECONFIG file to  |
|                   |                    | use for connection to Kubernetes               |
+-------------------+--------------------+------------------------------------------------+

When working with ``Minikube``, set ``KUBECONFIG`` in ``PrivateRules.mak`` as follows:

* ``KUBECONFIG = $(HOME)/.kube/config``

And then the correct ``KUBE_CONFIG_BASE64`` value can be automatically generated into ``PrivateRules.mak`` by running ``make kubeconfig``.


Running the tests
~~~~~~~~~~~~~~~~~

The following assumes that the available test environment is a local ``Minikube`` based Kubernetes cluster.  To run the tests, follow the workflow  on ``Minikube``:

Deploying a chart from a template:

* run ``make install-chart`` and check that the processes settle with ``make wait``
* execute the tests with ``make test`` - this will run the powersupply test suite
* teardown the test environment with ``make uninstall-chart``

Alternatively the entire process can be executed using gitlab-runner locally with ``make rk8s_test``.  This will launch the entire suite in a ``Namespace`` named after the current branch with the following steps:

* Set Namespace
* Install dependencies for Helm and kubectl
* Deploy Helm release into Namespace
* Run Helm tests
* Run test in run to completion Pod
* Extract Pod logs
* Set test return code
* Delete Helm release
* Delete namespace
* Return job step result

Test output is piped out of the test ``Pod`` and unpacked in the ``./build`` directory.

Deploy the `event-generator` device via a helm repo
===================================================

The `event-generator` device can be deployed by making use of a helm repository.

* Add the helm repository

::

  helm repo add tex https://gitlab.com/ska-telescope/tango-example/-/raw/master/helm-repo/

* If the repository has been loaded previously it can be updated

::

  helm repo update
  Hang tight while we grab the latest from your chart repositories...
  ...Successfully got an update from the "tex" chart repository

* Verify `event-generator` has been added

::

  helm search repo event-generator
  NAME               	CHART VERSION	APP VERSION	DESCRIPTION
  tex/event-generator	0.1.0        	1.0        	A Helm chart for deploying the Tango event gene...

* Install

::

  helm install <release_name>  tex/event-generator  -n <namespace>

* Set a different TANGO_HOST

You may want to override the Tango Host

::

  helm install <release_name>  tex/event-generator --set env.TANGO_HOST="<host:port>" -n <namespace>
