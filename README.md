Example Tango Project
=====================

This project demonstrates how to structure an SKA project that provides a simple 
Tango device coded in PyTango. 

This project builds upon the ska-skeleton 
example project, replacing the pure Python application with the PyTango
example device from the PyTango online documentation. The code in this 
repository shows how to build and test a Docker image containing the Tango 
device, and how the build and tests can be integrated with the SKA continuous 
integration server.

### Makefile targets
A makefile acts as a front-end to the building of Docker images, the testing 
of the images, and launching of interactive developer environments. The 
following make targets are defined:

- build: build a new application image;
- test: test the application image;
- interactive: launch a minimal Tango system including the device, mounting the 
  source directory from the host machine inside the container;
- piplock: overwrite the Pipfile.lock in the source directory with the generated version from a new application image;
- push: push the application image to the Docker registry;
- up: launch the development/test container service on which this application depends;
- down: stop all containers launched by 'make up' and 'make interactive';
- help: show a summary of all the makefile targets above.

To achieve the above, the following assumptions are enforced:

- Application code is located at /app inside the application image;
- The virtual environment for the application is located at /venv in the application image;
- All artefacts required for 'make test' are to be located in the test-harness directory (see test details).

### Creating a new application image
The 'make build' target creates a new Docker image for the application based on the 'ska-python' image. To support the addition of C extension Python libraries (e.g., Pytango), the image build procedure temporarily installs a compiler environment for the duration of 'Pipfile install' procedure before removing the compiler and associated dependencies from the final image.

### Modifying project dependencies
To permanently add, modify, or delete project dependencies, edit the Pipfile and run 'make piplock' to build a new application image containing the updated libraries. This procedure also copies the generated Pipfile.lock file across to the source directory. The resulting Pipfile.lock should be committed to VCS as it defines the specific library versions that this application is developed and tested against.

### Interactive development using containers
The 'make interactive' target launches an interactive session using the application image, mounting the project source directory at /app inside the container. This allows the container to run code from the developer's working directory. Any changes made to the project source code will immediately be seen inside the container.

### Service dependencies
The docker-compose.yml file should define the container services required to unit test the application. These services will be launched by 'make test' and by the CI service when testing the application. The example docker-compose.yml file defines a minimal Tango system; these services are not necessary for the pure Python application presented here but form a useful template for control system applications.

### Test execution
'make test' runs the application test procedure defined in test-harness/Makefile in a temporary container. The Makefile example for ska-skeleton runs 'python setup.py test' and copies the resulting output and test artefacts out of the container into a 'build' directory, ready for inclusion in the downloadable CI artefacts.

If running in an interactive session, the same tests can be run by executing 'make test' from inside the test-harness directory.


