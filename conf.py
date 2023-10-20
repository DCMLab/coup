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
exclude_patterns = [
    'build',
    'Thumbs.db',
    '.DS_Store',
    '**.ipynb',
    'README.md'
]




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

nb_execution_timeout = 120 # seconds
nb_execution_excludepatterns = [
    'notebooks/annotations.md',
    'notebooks/cadences.md',
    'notebooks/dft.md',
    'notebooks/keys.md',
    'notebooks/line_of_fifths.md',
    'notebooks/modulations_adapted_for_mozart.md',
    'notebooks/notes_stats.md',
    'notebooks/overview.md',
    'notebooks/scale_degrees.md',
]
