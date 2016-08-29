import os
from datetime import datetime

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# the github project name
project = 'mutils'

year = datetime.now().year
copyright = u'%d, The Mutopia Project' % year
author = 'Glen Larsen'

version = '1'
release = '1.0'

language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build']

pygments_style = 'sphinx'
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

html_theme = 'alabaster'

html_theme_options = {
    'logo': 'mutopia-logo.svg',
    'logo_name': False,
    'fixed_sidebar': True,
}

#html_logo = 'graphics/mutopia-logo.svg'
html_favicon = 'graphics/favicon.ico'

html_static_path = ['_static', 'graphics', ]

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

musite_path = os.path.abspath('../../musite/docs/_build/html')
intersphinx_mapping = { 'python': ('https://docs.python.org/3', None),
                        'musite': (musite_path, None), }
