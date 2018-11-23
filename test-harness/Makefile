all: test

test:
    # wait for the device to be available before beginning the test
	retry -- tango_admin --check-device test/power_supply/1
	cd /app && python setup.py test | tee test_output.log
	# A temporary volume is mounted at /build when 'make test' is executing.
	# The following steps copy across useful output to this volume which can
	# then be extracted to form the CI summary for the test procedure.
	if [ -d /build ]; then \
		mv /app/test_output.log /build; \
		mv /app/htmlcov /build; \
		mv /app/coverage.xml /build; \
	fi;

.PHONY: all test
