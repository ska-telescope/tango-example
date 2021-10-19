# Use bash shell with pipefail option enabled so that the return status of a
# piped command is the value of the last (rightmost) commnand to exit with a
# non-zero status. This lets us pipe output into tee but still exit on test
# failures.
SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c

MARK ?= fast## this variable allow the mark parameter in the pytest
FILE ?= ##this variable allow to execution of a single file in the pytest
SLEEPTIME ?= 1200s ##amount of sleep time for the smoketest target
COUNT ?= 1## amount of repetition for pytest-repeat


all: test

.PHONY: test

test:
	echo "Inside the test"
	pip3 install -r requirements.txt
	mkdir -p build && \
	find . -name "*.pyc" -type f -delete && \
	ls -latr /app/src; \
	find /app/src; \
	PYTHONPATH=/app:/app/tests:/app/src:/app/src/ska_tango_examples pytest $(if $(findstring all,$(MARK)),, -m $(MARK)) --disable-pytest-warnings | tee pytest.stdout; \
	status=$$?; \
	echo "test: status is ($$status)"; \
	exit $$status
