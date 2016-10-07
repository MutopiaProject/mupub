"""mupub module
"""

__all__ = (
    '__title__', '__summary__', '__version__',
    '__author__', '__license__', '__copyright__'
)


__title__ = 'mupub'
__summary__ = 'Musical score publishing utility for the Mutopia Project'
__version__ = '0.1.0'

__author__ = 'Glen Larsen and mutopia contributors'
__author_email__= 'glenl.glx@gmail.com'
__uri__ = 'http://mutopiaproject.org/'

__license__ = 'MIT'
__copyright__ = 'Copyright 2016 The Mutopia Project'

from .core import MUTOPIA_BASE, FTP_BASE, URL_BASE
from .core import id_from_footer
from .header import Loader, LYLoader, VersionLoader, SchemeLoader
from .header import RawLoader, Header
from .header import find_header
from .config import CONFIG_DICT, CONFIG_DIR
from .lily import LyLocator, LyVersion
from .exceptions import BadConfiguration
from .validate import Validator, DBValidator
from .commands.check import check
from .commands.init import init
from .commands.build import build
