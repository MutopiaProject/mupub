"""mupub module. This is only a test...
"""

__all__ = (
    '__title__', '__summary__', '__version__',
    '__author__', '__license__', '__copyright__',
)


__title__ = 'mupub'
__summary__ = 'Musical score publishing utility for the Mutopia Project'

"""Versioning:
This utility follows a MAJOR . MINOR . EDIT format. Upon a major
release, the MAJOR number is incremented and the MINOR is zeroed.
During development of an upcoming release, the MINOR number may be
incremented.

"""
__version__ = '0.2.5'

__author__ = 'Glen Larsen and mutopia contributors'
__author_email__= 'glenl.glx@gmail.com'
__uri__ = 'http://mutopiaproject.org/'

__license__ = 'MIT'
__copyright__ = 'Copyright 2016 The Mutopia Project'

from .assets import collect_assets
from .commands.build import build
from .commands.check import check
from .commands.init import init
from .commands.tag import tag
from .commands.clean import clean
from .config import CONFIG_DICT, CONFIG_DIR, getDBPath
from .config import UTCFormatter, test_config
from .core import MUTOPIA_BASE, FTP_BASE, URL_BASE
from .core import id_from_footer
from .exceptions import BadConfiguration, IncompleteBuild
from .header import Loader, LYLoader, VersionLoader, SchemeLoader
from .header import RawLoader, Header
from .header import find_header
from .lily import LyLocator, LyVersion
from .validate import Validator, DBValidator
from .tagedit import tag_header, tag_file
from .rdfu import NS, MuRDF
