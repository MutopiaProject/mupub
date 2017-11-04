"""Publishing module, implementing the build entry point.

This command is entered using the mupub command and may be as simple as, ::

  $ mupub build


"""

import argparse
import glob
import logging
import os
import subprocess
from clint.textui import colored, puts
import mupub

def _remove_if_exists(path):
    if os.path.exists(path):
        os.unlink(path)


def _stripped_base(infile):
    basefnm = os.path.basename(infile)
    return basefnm[:basefnm.rfind('.')]


def _build_scores(base_params, infile):
    """Build scores in the required page sizes.

    :param base_params: List of LilyPond command and params.
    :param infile: The file to compile.

    """
    logger = logging.getLogger(__name__)

    pagedef = {'a4': 'a4', 'letter': 'let'}
    build_params = ['--format=pdf', '--format=ps',]
    basefnm = _stripped_base(infile)

    for psize in pagedef.keys():
        puts(colored.green('Building score, page size = ' + psize))
        command = base_params + build_params
        command.append('-dpaper-size="{}"'.format(psize))
        command.append(infile)
        try:
            subprocess.check_output(command)
        except subprocess.CalledProcessError as cpe:
            logging.error('LilyPond returned an error code of %d' % cpe.returncode)
            return False

        # rename the pdf and ps files to include their page size
        pdf_fnm = basefnm + '.pdf'
        if os.path.exists(pdf_fnm):
            sized_pdf = basefnm + '-{0}.pdf'.format(pagedef[psize])
            os.rename(pdf_fnm, sized_pdf)

        ps_fnm = basefnm + '.ps'
        if os.path.exists(ps_fnm):
            sized_ps = basefnm + '-{0}.ps'.format(pagedef[psize])
            os.rename(ps_fnm, sized_ps)

    return True


def _build_preview(base_params, lpversion, infile, force_png_preview=False):
    """Build a preview file

    :param base_params: Starting list of LilyPond command and parameters.
    :param lpversion: The LilyPond version of the source file.
    :param infile: LilyPond file to compile.
    :force_png_preview: Force the use of PNG format in preview
    """

    logger = logging.getLogger(__name__)
    preview_params = [] # '-dno-include-book-title-preview',]

    if lpversion < mupub.LyVersion('2.14'):
        base_params.append('-dresolution=101'),
        base_params.append('--preview')
        base_params.append('--no-print')
        base_params.append('--format=png')
    else:
        base_params.append('-dno-print-pages'),
        base_params.append('-dpreview')
        if force_png_preview:
            base_params.append('--format=png')
        else:
            base_params.append('-dbackend=svg')

    command = base_params + preview_params
    command.append(infile)
    puts(colored.green('Building preview and midi'))
    try:
        subprocess.check_output(command)
    except subprocess.CalledProcessError as cpe:
        logging.error('LilyPond returned an error code of %d' % cpe.returncode)
        return False

    return True


def _build_one(infile, lily_path, lpversion, do_preview, force_png_preview=False):
    """Build a single lilypond file.

    :param infile: LilyPond file to build, might be None
    :param lily_path: Path to LilyPond build script
    :param do_preview: Boolean to flag additional preview build
    :param force_png_preview: Force use of PNG format in preview

    """

    base, infile = mupub.utils.resolve_input(infile)
    if not infile:
        puts(colored.red('Failed to resolve infile %s' % infile))
        return

    base_params = [lily_path, '-dno-point-and-click',]

    if _build_scores(base_params, infile):
        if do_preview:
            _build_preview(base_params, lpversion, infile, force_png_preview)


def _lily_build(infile, header, force_png_preview=False):
    lpversion = mupub.LyVersion(header.get_value('lilypondVersion'))
    locator = mupub.LyLocator(str(lpversion), progress_bar=True)
    lily_path = locator.working_path()

    # Build each score, doing a preview on the first one only.
    do_preview = True
    for ly_file in infile:
        _build_one(ly_file, lily_path, lpversion, do_preview, force_png_preview)
        do_preview = False


def build(infile,
          header_file,
          collect_only=False,
          skip_header_check=False,
          force_png_preview=False ):
    """Build one or more |LilyPond| files, generate publication assets.

    :param infile: The |LilyPond| file(s) to build.
    :param header_file: The file containing the header information.
    :param collect_only: Skip building, just collect assets and build RDF.
    :param skip_header_check: Skip header validation.
    :param force_png_preview: Coerce PNG format in preview

    This command presumes your current working directory is the
    location where the contributed source files live in the
    MutopiaProject hierarchy. A successful build will create all
    necessary assets for publication.

    """
    logger = logging.getLogger(__name__)
    logger.info('build command starting')
    base, lyfile = mupub.utils.resolve_input()

    if not mupub.commands.init.verify_init():
        return

    if len(infile) < 1:
        if lyfile:
            infile.append(lyfile)
        else:
            logger.error('Failed to resolve any input files.')
            logger.info('Make sure your working directory is correct.')
            return

    # if a header file was given, use that for reading the header,
    # else infile.
    if header_file:
        header_file = mupub.resolve_lysfile(header_file)
        header = mupub.find_header(header_file)
    else:
        header = mupub.find_header(infile[0])

    if not header:
        puts(colored.red('failed to find header'))
        return

    # Try to handle missing required fields.
    if not header.is_valid():
        mfields = header.missing_fields()
        if len(mfields) > 0:
            logger.warning('Invalid header, missing: %s' % mfields)
        if skip_header_check:
            puts(colored.yellow('Header not complete, continuing.'))
        else:
            # return without building otherwise
            puts(colored.red('Header validation failed.'))
            logger.debug('Incorrect or incomplete header.')
            return

    if not collect_only:
        _lily_build(infile, header, force_png_preview)

    # rename all .midi files to .mid
    for mid in glob.glob('*.midi'):
        os.rename(mid, mid[:len(mid)-1])

    assets = mupub.collect_assets(base)
    puts(colored.green('Creating RDF file'))
    header.write_rdf(base+'.rdf', assets)

    # remove by-products of build
    _remove_if_exists(base+'.ps')
    _remove_if_exists(base+'.png')
    _remove_if_exists(base+'.preview.png')
    _remove_if_exists(base+'.preview.svg')
    _remove_if_exists(base+'.preview.eps')
    logger.debug('Publishing build complete.')


def main(args):
    """Module entry point for the build command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub build')
    parser.add_argument(
        'infile',
        nargs='*',
        default=[],
        help='LilyPond input file (try to work it out if not given)'
    )
    parser.add_argument(
        '--header-file',
        help='LilyPond file that contains the header'
    )
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='Collect built files into publishable assets'
    )
    parser.add_argument(
        '--skip-header-check',
        action='store_true',
        help='Do not exit on failed header validation'
    )
    parser.add_argument(
        '--force-png-preview',
        action='store_true',
        help='Force a preview with PNG format instead of default SVG'
    )

    args = parser.parse_args(args)
    build(**vars(args))
