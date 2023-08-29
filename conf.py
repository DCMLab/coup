# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Coup'
copyright = '2023, Johannes Hentschel'
author = 'Johannes Hentschel'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.githubpages',
    "myst_nb", # rendering Jupyter notebooks
    "jupyter_sphinx", # rendering interactive Plotly in notebooks
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'myst-nb',
}

templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store', '**.ipynb', 'README.md']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
