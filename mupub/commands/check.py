"""The check entry point for mupub
"""

__docformat__ = 'reStructuredText'

import argparse
import logging
import os
import sqlite3
from clint.textui import colored, puts, indent
import mupub


def check(infile, header_file):
    """Check sanity for a given contributed file.

    :param [str] infile: Input file list.
    :param str header_file: The file containing the header.

    The routine does not return True or False, but simply reports
    information on various checks made to the input files. This should
    be run prior to any build.

    """
    logger = logging.getLogger(__name__)

    base, infile = mupub.resolve_input(infile)

    if not mupub.commands.init.verify_init():
        return

    if header_file:
        header_file = mupub.resolve_lysfile(header_file)
        logger.debug('Searching %s for header', header_file)
        logger.info('check command starting for %s.' % header_file)
        try:
            header = mupub.find_header(header_file)
        except FileNotFoundError as fnf:
            logger.error(fnf)
            return
    else:
        header = mupub.find_header(infile)

    if not header:
        logger.warning('Partial or no header content found')
        return

    with sqlite3.connect(mupub.getDBPath()) as conn:
        validator = mupub.DBValidator(conn)
        v_failures = validator.validate_header(header)
        if len(v_failures) > 0:
            puts(colored.red('Failed validation on:'))
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
            if path:
                puts(colored.green('LilyPond compiler will be %s' % path))
            else:
                puts(colored.red('Failed to determine (or install) compiler.'))
        except mupub.BadConfiguration as bc:
            logger.warning(bc)
            return

    logger.info('%s is valid' % infile)


def main(args):
    """Check entry point.
    """
    logger = logging.getLogger(__name__)

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
