"""Tagging module, implementing the tag entry point.
"""

import argparse
import os
from clint.textui import colored, puts
import mupub
import tempfile

def tag(header_file, id):
    if not header_file:
        _,header_file = mupub.utils.resolve_input()
        puts(colored.yellow('tag target is %s.' % header_file))

    # Start with loading the header as a table
    htable = mupub.LYLoader().load(header_file)
    if not htable:
        puts(colored.red('No header found for %s.' % header_file))
        return

    outfnm = ''
    with tempfile.NamedTemporaryFile(mode='w',
                                     suffix='.ly',
                                     prefix='mu_',
                                     delete=False) as outfile:
        outfnm = outfile.name
        with open(header_file, mode='r', encoding='utf-8') as infile:
            mupub.tag_header(infile, outfile, htable, id)

    # header_file is closed, rename it to a backup file and create
    # a new file with the same contents as the temporary output file.
    backup = header_file+'~'
    if os.path.exists(backup):
        os.unlink(backup)
    os.rename(header_file, backup)
    with open(outfnm, 'r', encoding='utf-8') as tmpf:
        with open(header_file, mode='w', encoding='utf-8') as tagged_file:
            for line in tmpf:
                tagged_file.write(line)
    os.unlink(outfnm)


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
