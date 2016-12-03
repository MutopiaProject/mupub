"""Implementation of check entry point for mupub
"""

__docformat__ = 'reStructuredText'

import argparse
import logging
import os
import sys
import sqlite3
from clint.textui import colored, puts
import mupub
from mupub.config import CONFIG_DICT, DBPATH

logger = logging.getLogger(__name__)

def check(infile, header_file):
    """Check sanity for a given input file.
    """
    logger.debug('check command starting')
    base, infile = mupub.utils.resolve_input(infile)
    if not infile:
        logger.debug('File resolution failed')
        puts(colored.red('Failed to resolve input file'))
        return

    if header_file:
        logger.debug('Searching %s for header', header_file)
        header = mupub.find_header(header_file)
    else:
        logger.debug('Searching %s for header', infile)
        header = mupub.find_header(infile)

    if not header:
        logger.debug('No header found?')
        puts(colored.red('failed to find header'))
        return

    with sqlite3.connect(DBPATH) as conn:
        validator = mupub.DBValidator(conn)
        if not validator.validate_header(header, True):
            puts(colored.red('{} failed validation'.format(infile)))
            return

        lp_version = header.get_value('lilypondVersion')
        puts(colored.green('{} is valid'.format(infile)))
        puts(colored.green('This file uses LilyPond version '
                               + lp_version))
        locator = mupub.LyLocator(lp_version)
        path = locator.working_path()

        puts(colored.green('LilyPond compiler will be ' + path))


def main(args):
    """Check entry point.
    """
    parser = argparse.ArgumentParser(prog='mupub check')
    parser.add_argument(
        'infile',
        nargs='?',
        help='lilypond input file (try to work it out if not given)'
    )
    parser.add_argument(
        '--header-file',
        help='lilypond file that contains the header'
    )

    args = parser.parse_args(args)

    check(**vars(args))
