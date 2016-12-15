"""Implementation of check entry point for mupub
"""

__docformat__ = 'reStructuredText'

import argparse
import logging
import os
import sys
import sqlite3
from clint.textui import colored, puts, indent
import mupub
from mupub.config import CONFIG_DICT, getDBPath

logger = logging.getLogger(__name__)

def check(infile, header_file):
    """Check sanity for a given input file.
    """
    base, infile = mupub.utils.resolve_input(infile)
    logger.info('check command starting for %s.' % infile)
    if not mupub.commands.init.verify_init():
        return

    if not infile:
        logger.warning('File resolution failed')
        return

    if header_file:
        logger.debug('Searching %s for header', header_file)
        header = mupub.find_header(header_file)
    else:
        logger.debug('Searching %s for header', infile)
        header = mupub.find_header(infile)

    if not header:
        logger.warning('No header found?')
        return

    with sqlite3.connect(getDBPath()) as conn:
        validator = mupub.DBValidator(conn)
        v_failures = validator.validate_header(header)
        if len(v_failures) > 0:
            puts(colored.red('{} failed validation on:'.format(infile)))
            with indent(4):
                for fail in v_failures:
                    puts(colored.red(fail))
            return

        lp_version = header.get_value('lilypondVersion')
        if not lp_version:
            logger.warning('No LilyPond version found in input file.')
            return

        try:
            locator = mupub.LyLocator(lp_version, progress_bar=True)
            path = locator.working_path()
            puts(colored.green('LilyPond compiler will be ' + path))
        except mupub.BadConfiguration as bc:
            logger.warning(bc)
            return

    logger.info('%s is valid' % infile)


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

    mupub.config.test_config()
    args = parser.parse_args(args)

    check(**vars(args))
