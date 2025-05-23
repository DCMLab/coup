# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Coup'
copyright = '2025, Johannes Hentschel'
author = 'Johannes Hentschel'
release = 'v2.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb", # rendering Jupyter notebooks
    "jupyter_sphinx", # rendering interactive Plotly in notebooks
]

templates_path = ['_templates']
exclude_patterns = [
    'build',
    'Thumbs.db',
    '.DS_Store',
    '**.ipynb',
    '**README.md',
    'notebooks/accents*',
    'notebooks/annotations*',
    'notebooks/cadences*',
    'notebooks/cross*',
    'notebooks/dft*',
    'notebooks/information*',
    'notebooks/ismir*',
    'notebooks/keys*',
    'notebooks/line_of_fifths*',
    'notebooks/*mozart*',
    'notebooks/notes_stats*',
    'notebooks/overview*',
    'notebooks/reduction*',
    'notebooks/specific*'
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_css_files = [
    'custom.css',
]

# -- MyST Notebook configuration-----------------------------------------------
# https://myst-nb.readthedocs.io/en/latest/configuration.html

nb_execution_mode = "cache"
nb_execution_timeout = 300
nb_execution_allow_errors = False
nb_execution_show_tb = True
# toggle text:
nb_code_prompt_show = "Show {type}"
nb_code_prompt_hide = "Hide {type}"