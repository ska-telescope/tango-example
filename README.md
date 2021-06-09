# tango-example

[![Documentation Status](https://readthedocs.org/projects/tango-example/badge/?version=latest)](https://developer.skatelescope.org/projects/tango-example/en/latest/?badge=latest)

This project demonstrates how to structure an SKA project that provides some simple Tango devices coded in PyTango. 

Documentation can be found in the ``docs`` folder.

## Installation

This project is structured to use k8s for development and testing so that the build environment, test environment and test results are all completely reproducible and are independent of host environment. It uses ``make`` to provide a consistent UI (run ``make help`` for targets documentation).

### Install docker

Follow the instructions available at [here](https://docs.docker.com/get-docker/).

### Install minikube

You will need to install `minikube` or equivalent k8s installation in order to set up your test environment. You can follow the instruction at [here](https://gitlab.com/ska-telescope/sdi/deploy-minikube/):
```
git clone git@gitlab.com:ska-telescope/sdi/deploy-minikube.git
cd deploy-minikube
make all
eval $(minikube docker-env)
```

## How to Use

Clone this repo: 
```
git clone git@gitlab.com:ska-telescope/tango-example.git
cd tango-example
```

Create a virtualenv:
```
virtualenv venv
source venv/bin/activate
```

Build a new Docker image for the project:
```
$ make build
[...]
[+] Building 111.7s (14/14) FINISHED 
[...]
```

Install python requirements for linting and unit testing:
```
$ make requirements
python3 -m pip install -r requirements.txt
Looking in indexes: https://pypi.org/simple, https://nexus.engageska-portugal.pt/repository/pypi/simple
Requirement already satisfied: numpy==1.19.2 in ./venv/lib/python3.8/site-packages (from -r requirements.txt (line 2)) (1.19.2)
Requirement already satisfied: pytango>=9.3.3 in ./venv/lib/python3.8/site-packages (from -r requirements.txt (line 3)) (9.3.3)

```

Run unit-test:
```
$ make unit_test
PyTango 9.3.3 (9, 3, 3)
PyTango compiled with:
    Python : 3.8.5
    Numpy  : 0.0.0 ## output generated from a WSL windows machine
    Tango  : 9.2.5
    Boost  : 1.71.0

PyTango runtime is:
    Python : 3.8.5
    Numpy  : None
    Tango  : 9.2.5

PyTango running on:
uname_result(system='Linux', node='LAPTOP-5LBGJH83', release='4.19.128-microsoft-standard', version='#1 SMP Tue Jun 23 12:58:10 UTC 2020', machine='x86_64', processor='x86_64')

============================= test session starts ==============================
platform linux -- Python 3.8.5, pytest-5.4.3, py-1.10.0, pluggy-0.13.1 -- /home/ubuntu/tango-example/venv/bin/python3
cachedir: .pytest_cache
metadata: {'Python': '3.8.5', 'Platform': 'Linux-4.19.128-microsoft-standard-x86_64-with-glibc2.29', 'Packages': {'pytest': '5.4.3', 'py': '1.10.0', 'pluggy': '0.13.1'}, 'Plugins': {'forked': '1.3.0', 'mock': '3.6.1', 'repeat': '0.9.1', 'metadata': '1.11.0', 'bdd': '4.0.2', 'cov': '2.12.1', 'xdist': '1.34.0', 'json-report': '1.3.0'}, 'JAVA_HOME': '/usr/lib/jvm/oracle_jdk8'}
rootdir: /home/ubuntu/tango-example, inifile: setup.cfg, testpaths: tests
plugins: forked-1.3.0, mock-3.6.1, repeat-0.9.1, metadata-1.11.0, bdd-4.0.2, cov-2.12.1, xdist-1.34.0, json-report-1.3.0
collecting ... collected 51 items

tests/integration/test_async_tabata.py::test_tabata 
[...]
- generated json file: /home/ubuntu/tango-example/build/reports/cucumber.json --
- generated xml file: /home/ubuntu/tango-example/build/reports/unit-tests.xml --
--------------------------------- JSON report ----------------------------------
JSON report written to: build/reports/report.json (165946 bytes)

----------- coverage: platform linux, python 3.8.5-final-0 -----------
Coverage HTML written to dir build/htmlcov
Coverage XML written to file build/reports/code-coverage.xml

======================== 48 passed, 3 xfailed in 43.21s ========================
```

Python linting:
```
$ make lint
[...]
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

pylint --output-format=pylint_junit.JUnitReporter src/* tests/* > build/reports/linting-python.xml
```

Helm Charts linting:
```
$ make chart_lint
[...]
10 chart(s) linted, 0 chart(s) failed
```

Install the umbrella chart:
```
$ make install-chart
[...]
NAME: test
LAST DEPLOYED: Tue Jun  8 22:37:03 2021
NAMESPACE: tango-example
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

Test the deployment with (not that in this case the result of the tests are stored into the folder ``charts/build``):
```
$ make test
tar -c tests/ | kubectl run test-makefile-runner--tango-example-test --namespace tango-example -i --wait --restart=Never --image-pull-policy=IfNotPresent --image=nexus.engageska-portugal.pt/ska-tango-images/tango-example:0.4.0-dirty -- /bin/bash -c "mkdir -p build; tar xv --directory tests --strip-components 1 --warning=all; pip install -r tests/requirements.txt; PYTHONPATH=/app/src:/app/src/ska_tango-examples KUBE_NAMESPACE=tango-example HELM_RELEASE=test TANGO_HOST=tango-host-databaseds-from-makefile-test:10000 pytest  --true-context  && tar -czvf /tmp/test-results.tgz build && echo '~~~~BOUNDARY~~~~' && cat /tmp/test-results.tgz | base64 && echo '~~~~BOUNDARY~~~~'" 2>&1; \
	status=$?; \
	rm -rf charts/build; \
	kubectl --namespace tango-example logs test-makefile-runner--tango-example-test | \
	perl -ne 'BEGIN {$on=0;}; if (index($_, "~~~~BOUNDARY~~~~")!=-1){$on+=1;next;}; print if $on % 2;' | \
	base64 -d | tar -xzf - --directory charts; \
	kubectl --namespace tango-example delete pod test-makefile-runner--tango-example-test; \
	exit $status
[...]
------------ generated json file: /app/build/reports/cucumber.json -------------
------------ generated xml file: /app/build/reports/unit-tests.xml -------------
--------------------------------- JSON report ----------------------------------
JSON report written to: build/reports/report.json (99140 bytes)

----------- coverage: platform linux, python 3.7.3-final-0 -----------
Coverage HTML written to dir build/htmlcov
Coverage XML written to file build/reports/code-coverage.xml

================== 48 passed, 1 xfailed, 2 xpassed in 15.06s ===================
```

Uninstall the chart: 
```
$ make uninstall-chart 
release "test" uninstalled
```

## Project structure

```
.
├── APACHE2-LICENSE
├── CHANGELOG.rst
├── COPYRIGHT
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── charts # contains the helm charts to be able to install the project into a k8s namespace
├── docs # documentation
├── requirements-dev.txt # pip requirements file for development
├── requirements.txt # pip requirements file for the application run-time
├── setup.cfg # setuptools
├── setup.py # setuptools
├── src # source folder
│   └── ska_tango_examples # main module
│       ├── DevFactory.py
│       ├── __init__.py
│       ├── basic_example
│       ├── counter
│       ├── tabata
│       └── teams
├── tests # tests folder
│   ├── __init__.py
│   ├── conftest.py
│   ├── integration
│   ├── requirements.txt
│   └── unit
```

## TANGO-controls examples

### Basic Example

The basic example is meant to demonstrate the change event with polling on attribute. 
It contains 3 devices called 'powersupply' (taken from  [here](https://pytango.readthedocs.io/en/stable/server_api/server.html).), "motor' and 'eventreceiver. It is contained into the folder ``src/ska_tango_example/basic_example``.

The motor uses the powersupply and generate a (random) performance value attribute which is polled (with automatic fire of the related change event). The eventreceiver receives that event. 

### Counter

The counter is an example of firing an event without a polled attribute. 

### Teams

This python package contains devices created and used by various SKA teams. Mainly they are used for testing other applications. 

### Tabata

The tabata is a realization of a gym workout (more information at [here](https://en.wikipedia.org/wiki/High-intensity_interval_training)).

An example of this application can be found [here](https://www.tabatatimer.com/).

The TANGO-controls concepts demonstrated are:
- use of device properties;
- handling of events coming from 5 other devices;
- managing a simple state attribute (DevState and RunningState);
- threading with TANGO. 

The tabata device has 2 commands: Start and Stop. The start trigger the decrement on the counters to perform its job. 

### AsyncTabata

Same as Tabata but the realization is asynchonous. 

The tabata device has 2 commands: Run and Stop. The run executes the entire job so it's not possible to use it without an async command.
The async device does not use the tango monitor, so lock is managed directly by the device. 

## TANGO References
* https://pytango.readthedocs.io/en/stable/contents.html
* https://pytango.readthedocs.io/en/stable/green_modes/green_modes_server.html
* https://pytango.readthedocs.io/en/stable/testing.html
* https://pytango.readthedocs.io/en/stable/client_api/index.html
* https://pytango.readthedocs.io/en/stable/server_api/server.html

## ska-tango-images

Please note that this project make use of the charts docker images for the TANGO-controls framework available at [here](https://gitlab.com/ska-telescope/ska-tango-images).

## Test execution

All tests created for the present project can run in simulated mode or in a real environment. 

``make test`` runs the application test procedures defined in the folder `tests` in a new pod in the k8s deployment. 
The Makefile example for this project runs the target ``make unit_test`` and copies the resulting output and test artefacts out of the container and into a 'build' directory, ready for inclusion in the CI server's downloadable artefacts.

``make unit_test`` runs the application test procedures defined in the folder `tests` without starting a new pod. For this reason it is important the use of a virtual env. 

## Debugging with vscode

In order to debug a device server, this project uses the library  [debugpy](https://github.com/microsoft/debugpy/). To be able to debug your code, just run the following command: 

::
  kubectl port-forward pods/eventreceiver-test-0 12345:5678 -n tango-example

The above command will create a port forwarding between the local machine and the event receiver pod. 

Once done open the Run tab on vscode and press the debug button which correspond to the launch.json configuration file ``Python: Remote Attach``. 

The ``.vscode`` folder contains also the settings to be able to run the pytest with the python extension. Note that it expects that a ``venv`` folder is present.

## Makefile targets

This project contains a Makefile which acts as a UI for building Docker images, testing images, and for launching interactive developer environments.
For the documentation of the Makefile run ``make help``.
