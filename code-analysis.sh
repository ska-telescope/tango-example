#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=setup.cfg module_example

echo "TESTS ANALYSIS"
echo "--------------"
pylint tests
