#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo

echo "Module analysis:"
pylint ska_skeleton

echo "Tests analysis:"
pylint tests
