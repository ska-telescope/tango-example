#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint module_example

echo "TESTS ANALYSIS"
echo "--------------"
pylint tests
