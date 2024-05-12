"""Functions and variable common to other modules."""
import cowsay
from importlib.resources import files
from . import custom_monsters


FIELD_SIZE = 10
"""Size of field."""

arsenal = {'sword': 10,
           'spear': 15,
           'axe': 20}
"""Types of weapon."""


def get_list_custom_cows():
    """Return list of custom cows."""
    return [file.name.partition('.')[0]
            for file in files(custom_monsters).iterdir()
            if file.is_file()]


def get_extended_list_cows():
    """Return list of default and custom cows."""
    arr = cowsay.list_cows()
    arr.extend(get_list_custom_cows())
    return arr


def get_custom_cow(cow):
    """Return custom cow from cowfile by name."""
    filename = cow + '.cow'
    with files(custom_monsters).joinpath(filename).open() as cow_file:
        res = cowsay.read_dot_cow(cow_file)
    return res
