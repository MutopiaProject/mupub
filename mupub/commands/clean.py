"""Clean module, implementing the clean entry point.
"""

import argparse
import glob
import os
from clint.textui import colored, puts

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

def clean(verbose, dry_run):
    """Clean all manifest files.

    :param verbose: Display additional information about deletions.
    :param dry_run: Don't actuall delete.

    """
    for deadset in _DEATHROW:
        for deadfile in glob.iglob(deadset):
            if dry_run:
                puts(colored.yellow('would delete {}'.format(deadfile)))
            else:
                os.unlink(deadfile)
                if verbose:
                    puts(colored.green('deleted {}'.format(deadfile)))


def main(args):
    """Entry point for clean command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub build')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Louder.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done but don't do it."
    )

    args = parser.parse_args(args)
    clean(**vars(args))
