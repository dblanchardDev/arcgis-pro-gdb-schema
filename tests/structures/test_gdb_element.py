"""Unit tests for Geodatabase Base class for structure."""
#pylint: disable=protected-access,missing-function-docstring

from gdbschematools.structures.gdb_element import GDBElement

def test_gdb_element_initialization():
    alpha = GDBElement("Alpha")
    assert alpha.name == "Alpha"


def test_gdb_element_representation():
    alpha = GDBElement("Alpha")
    assert alpha._element_type == "gdbelement"
    assert repr(alpha) == "<structures.GDBElement name='Alpha'>"


def test_gdb_element_sorting():
    alpha = GDBElement("Alpha")
    beta = GDBElement("Beta")
    assert alpha < beta
    assert (beta < alpha) is False