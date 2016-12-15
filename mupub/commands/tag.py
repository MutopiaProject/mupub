"""Tagging module, implementing the tag entry point.
"""

import argparse
import logging
import mupub

def tag(header_file, id):
    logger = logging.getLogger(__name__)
    if not header_file:
        _,header_file = mupub.utils.resolve_input()
        logger.info('tag target is %s.' % header_file)

    logger.info('tag command starting with %s' % header_file)
    mupub.tag_file(header_file, id)


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
        default=0,
        help='Integer portion of the Mutopia identifier'
    )

    args = parser.parse_args(args)
    tag(**vars(args))
