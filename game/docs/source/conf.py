import pathlib
import sys

sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

project = 'MOOD'
copyright = '2024, Maria B'
author = 'Maria B'


extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']
