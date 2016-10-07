"""Implementation of check entry point for mupub
"""

__docformat__ = 'reStructuredText'

import argparse
import os
import sys
import psycopg2
from clint.textui import colored, puts
import mupub
from mupub.config import CONFIG_DICT


def check(infile, header_file, database, debug=False):
    """Check sanity for a given file.
    """

    if database not in CONFIG_DICT:
        print('Invalid database name - ' + database)
        return

    base, infile = mupub.utils.resolve_input(infile)
    if not infile:
        puts(colored.red('Failed to resolve input file'))
        return
    
    if not infile:
        puts(colored.red('Failed to resolve input file'))
        return

    if header_file:
        header = mupub.find_header(header_file)
    else:
        header = mupub.find_header(infile)

    if not header:
        print('failed to find header')
        return

    db_dict = CONFIG_DICT[database]
    try:
        conn = psycopg2.connect(database=db_dict['name'],
                                user=db_dict['user'],
                                host=db_dict['host'],
                                port=db_dict['port'],
                                password=db_dict['password']
                                ,)
        validator = mupub.DBValidator(conn)
        if not validator.validate_header(header):
            print('{} failed validation'.format(infile))
            return

        lp_version = header.get_value('lilypondVersion')
        print('{} is valid'.format(infile))
        print('This file uses LilyPond version ' + lp_version)
        locator = mupub.LyLocator(lp_version)
        path = locator.working_path()

        print('LilyPond compiler will be ' + path)

    finally:
        conn.close()


def main(args):
    """Check entry point.
    """
    parser = argparse.ArgumentParser(prog='mupub check')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='play louder'
    )
    parser.add_argument(
        '--database',
        default='default',
        help='Database to use (defined in config)'
    )
    parser.add_argument(
        '--infile',
        help='lilypond input file (try to work it out if not given)'
    )
    parser.add_argument(
        '--header-file',
        help='lilypond file that contains the header'
    )

    args = parser.parse_args(args)

    check(**vars(args))
