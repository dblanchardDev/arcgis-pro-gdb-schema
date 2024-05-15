"""Unit tests for the base Interface class."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import pytest

from gdbschematools.interfaces.interface import BaseInterface


def test_not_implemented_on_read():
    with pytest.raises(NotImplementedError):
        BaseInterface.read("my invalid path")


def test_not_implemented_on_write():
    with pytest.raises(NotImplementedError):
        BaseInterface.write(object())