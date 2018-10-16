#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the ska_skeleton module.
"""
import pytest

from ska_skeleton import ska_skeleton


# FIXME: Replace all the following examples with tests for the ska_skeleton package code
def test_something():
    assert True


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise(ValueError)


# Fixture example
@pytest.fixture
def an_object():
    return {}


def test_ska_skeleton(an_object):
    assert an_object == {}


# Test the ska_skeleton package code
def test_package():
    assert ska_skeleton.example() is None
    assert ska_skeleton.testing_example() == 2
