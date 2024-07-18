import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('..'))

import mupub

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# the github project name
project = 'mupub'

year = datetime.now().year
copyright = u'%d, The Mutopia Project' % year
author = 'Glen Larsen'

# The short X.Y version.
version = '.'.join(mupub.__version__.split('.')[:2])
# The full version, including alpha/beta/rc tags.
release = mupub.__version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

pygments_style = 'sphinx'
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if on_rtd:
    musite_path = 'http://mudev-documentation.readthedocs.io/en/latest/'
else:
    html_theme = 'sphinx_rtd_theme'
    musite_path = os.path.abspath('../../musite/docs/_build/html')

html_favicon = 'graphics/favicon.ico'

html_static_path = ['_static', 'graphics', ]

#                        'musite': (musite_path, None),

intersphinx_mapping = { 'python': ('https://docs.python.org/3.12', None),
}
