# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Cliente INDIGO'
copyright = '2025, Arturo Arellano Romo'
author = 'Arturo Arellano Romo'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'env_indigo', 'env_indigo/*']
language = 'es'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

autodoc_typehints = 'description'