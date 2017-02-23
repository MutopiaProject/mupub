"""Clean module, implementing the clean entry point.
"""

import argparse
import glob
import logging
import os
from clint.textui import colored, puts
import mupub

logger = logging.getLogger(__name__)

_DEATHROW = [
    '*.preview.*',
    '*-preview.*',
    '*.mid',
    '*.midi',
    '*-mids.zip',
    '*.pdf',
    '*-pdfs.zip',
    '*.ps.gz',
    '*-pss.zip',
    '*-lys.zip',
    '*.rdf',
    '*.log',
]


def clean(dry_run):
    """Clean all built assets.

    :param verbose: Display additional information about deletions.
    :param dry_run: List delete candidates but don't delete.

    """
    if not mupub.in_repository('.'):
        logger.warn('Cannot clean in non-repository folder')
        return

    for deadset in _DEATHROW:
        for deadfile in glob.iglob(deadset):
            if dry_run:
                puts(colored.yellow('would delete {}'.format(deadfile)))
            else:
                os.unlink(deadfile)
                logger.debug('deleted %s' % deadfile)


def main(args):
    """Entry point for clean command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub build')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done but don't do it."
    )

    args = parser.parse_args(args)
    clean(**vars(args))
