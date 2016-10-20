"""Publishing module, implementing the build entry point.
"""

import argparse
import os
import subprocess
from clint.textui import colored, puts
import mupub
from mupub.config import CONFIG_DICT


def _remove_if_exists(path):
    if os.path.exists(path):
        os.unlink(path)


def _stripped_base(infile):
    basefnm = os.path.basename(infile)
    return basefnm[:basefnm.rfind('.')]


def build_scores(base_params, infile):
    """Build scores in the required page sizes.

    :param base_params: List of LilyPond command and params.
    :param infile: The file to compile.

    """

    pagedef = {'a4': 'a4', 'letter': 'let'}
    build_params = ['--format=pdf', '--format=ps',]
    basefnm = _stripped_base(infile)

    for psize in pagedef.keys():
        puts(colored.green('Building score, page size = ' + psize))
        command = base_params + build_params
        command.append('-dpaper-size="{}"'.format(psize))
        command.append(infile)
        subprocess.run(command, stdout=subprocess.PIPE)

        # rename the pdf
        pdf_fnm = basefnm + '.pdf'
        if os.path.exists(pdf_fnm):
            sized_pdf = basefnm + '-{0}.pdf'.format(pagedef[psize])
            os.rename(pdf_fnm, sized_pdf)

        ps_fnm = basefnm + '.ps'
        if os.path.exists(ps_fnm):
            sized_ps = basefnm + '-{0}.ps'.format(pagedef[psize])
            os.rename(ps_fnm, sized_ps)


def build_preview(base_params, infile):
    """Build a preview file

    :param base_params: Starting list of LilyPond command and parameters.
    :param infile: LilyPond file to compile

    """
    preview_params = ['-dno-print-pages',
                      '-dno-include-book-title-preview',
                      '-dresolution=72',
                      '-dpreview',
                      '--format=png',]

    basefnm = _stripped_base(infile)
    command = base_params + preview_params
    command.append(infile)
    puts(colored.green('Building preview and midi'))
    subprocess.run(command, stdout=subprocess.PIPE)

    # cleanup excess files
    _remove_if_exists(basefnm + '.preview.eps')


def build_rdf(header, base, assets):
    if os.path.exists(base+'-lys'):
        rdf_path = rdf_path[:rdf_path.rfind('.')] + '-lys.rdf'
    else:
        rdf_path = base + '.rdf'
    header.writeRDF(rdf_path, assets)


def build_one(infile, lily_path, do_preview, verbose=False):
    """Primary entry point for the build entry point.

    :param verbose: True for verbose output.
    :param database: Name of database entry in configuration.
    :param infile: LilyPond file to build, might be None

    """

    base, infile = mupub.utils.resolve_input(infile)
    if not infile:
        puts(colored.red('Failed to resolve input file'))
        return

    base_params = [lily_path,
                   '--loglevel=BASIC_PROGRESS',
                   '-dmidi-extension="mid"',
                   '-dno-point-and-click',]

    build_scores(base_params, infile)
    if do_preview:
        build_preview(base_params, infile)



def lily_build(verbose, database, infile, header):
    # The database name should be a name in the configuration file.
    # It would be difficult to make this a choice selection in the
    # argument parser so just check early and exit if necessary.
    if database not in CONFIG_DICT:
        puts(colored.red('Invalid database name - ' + database))
        return

    locator = mupub.LyLocator(header.get_value('lilypondVersion'))
    lily_path = locator.working_path()

    # Build each score, doing a preview on the first one only.
    do_preview = True
    for ly_file in infile:
        build_one(ly_file, lily_path, do_preview, verbose)
        do_preview = False


def build(verbose, database, infile, header_file, collect_only):
    if len(infile) < 1:
        _, lyfile = mupub.utils.resolve_input()
        infile.append(lyfile)

    if header_file:
        header = mupub.find_header(header_file)
    else:
        header = mupub.find_header(infile[0])

    if not header:
        puts(colored.red('failed to find header'))
        return

    if not header.is_valid():
        puts(colored.red('Validation failed.'))
        return

    if not collect_only:
        lily_build(verbose, database, infile, header)

    assets = mupub.collect_assets(infile[0])
    puts(colored.green('Creating RDF file'))
    header.writeRDF(os.path.basename(os.path.abspath('.'))+'.rdf', assets)


def main(args):
    """Module entry point for the build command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub build')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Louder.'
    )
    parser.add_argument(
        '--database',
        default='default',
        help='Database to use (defined in config)'
    )
    parser.add_argument(
        'infile',
        nargs='*',
        default=[],
        help='lilypond input file (try to work it out if not given)'
    )
    parser.add_argument(
        '--header-file',
        help='lilypond file that contains the header'
    )
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='collect built files into publishable assets')

    args = parser.parse_args(args)
    build(**vars(args))
