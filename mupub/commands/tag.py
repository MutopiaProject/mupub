"""Tagging module, implementing the tag entry point.
"""

import argparse
import logging
from clint.textui import colored, puts
import mupub


def tag(header_file, new_id, query):
    """Modify the header with a new id and publish date.

    :param str header_file: The file containing the header to modify.
    :param int new_id: New numeric identifier, unique to piece.
    """
    logger = logging.getLogger(__name__)
    if not header_file:
        _,header_file = mupub.utils.resolve_input()
        logger.info('tag target is %s.' % header_file)

    logger.info('tag command starting with %s' % header_file)
    try:
        mupub.tag_file(header_file, new_id, query)
    except mupub.TagProcessException:
        puts(colored.yellow('Tagging aborted, no changes made.'))


def main(args):
    """Entry point for clean command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub build')
    parser.add_argument(
        '--header-file',
        help='lilypond file that contains the header'
    )
    parser.add_argument(
        '--id',
        type=int,
        dest='new_id',
        default=0,
        help='Force identifier to this value (danger!)'
    )
    parser.add_argument(
        '--no-query',
        action='store_true',
        default=False,
        dest='query',
        help='Skip verification prompt.'
    )

    args = parser.parse_args(args)
    tag(**vars(args))
