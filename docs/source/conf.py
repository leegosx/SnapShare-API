# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os

sys.path.append(os.path.abspath('..'))

project = 'SnapShare-API'
copyright = '2023, 1. Dmytro Klymenko, 2. Dmytro Filin, 3. Dmytro Paukov, 4. Illya Hryhoriev'
author = '1. Dmytro Klymenko, 2. Dmytro Filin, 3. Dmytro Paukov, 4. Illya Hryhoriev'
release = '24/11/2023'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']
