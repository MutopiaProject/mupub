"""Publishing module, implementing the build entry point.
"""

import argparse
import glob
import gzip
import os
import png
import shutil
import subprocess
import sys
import zipfile
from clint.textui import colored, puts
import mupub
from mupub.config import CONFIG_DICT


def _remove_if_exists(path):
    if os.path.exists(path):
        os.unlink(path)


def _collect_lyfile(infile):
    dir_name = os.path.dirname(infile)
    if dir_name == '':
        # nothing to zip
        return infile

    if dir_name.endswith('-lys'):
        zip_name = os.path.basename(dir_name) + '.zip'
        puts(colored.green('Zipping source files into '+zip_name))
        with zipfile.ZipFile(zip_name, 'w') as lyzip:
            for folder in os.listdir(dir_name):
                lyzip.write(os.path.join(dir_name, folder))
        return zip_name


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


def _zip_maybe(basefnm, tail, ziptail):
    files = glob.glob('*'+tail)
    if len(files) == 1:
        single_file = basefnm+tail
        if files[0] != single_file:
            os.rename(files[0], single_file)
        # single ps files get compressed
        if tail.endswith('.ps'):
            gzipped_name = single_file+'.gz'
            with open(single_file, 'rb') as ps_in:
                with gzip.open(gzipped_name, 'wb') as gz_out:
                    shutil.copyfileobj(ps_in, gz_out)
            os.unlink(single_file)
            return gzipped_name
        else:
            return single_file
    else:
        zip_name = basefnm+ziptail
        puts(colored.green('Zipping files into '+zip_name))
        with zipfile.ZipFile(zip_name, 'w') as outzip:
            for file_to_zip in files:
                outzip.write(file_to_zip)
        for zipped_file in files:
            os.unlink(zipped_file)
        return zip_name
        

def collect_assets(infile):
    assets = {}
    basefnm = os.path.basename(os.path.abspath('.'))
    assets['lyFile'] = _collect_lyfile(infile)
    assets['midFile'] = _zip_maybe(basefnm, '.mid', '-mids.zip')
    assets['psFileA4'] = _zip_maybe(basefnm, '-a4.ps', '-a4-pss.zip')
    assets['psFileLet'] = _zip_maybe(basefnm, '-let.ps', '-let-pss.zip')
    assets['pdfFileA4'] = _zip_maybe(basefnm, '-a4.pdf', '-a4-pdfs.zip')
    assets['pdfFileLet'] = _zip_maybe(basefnm, '-let.pdf', '-let-pdfs.zip')

    # process the preview image
    pngfiles = glob.glob('*.preview.png')
    preview_name = basefnm + '-preview.png'
    if len(pngfiles) == 1:
        if pngfiles[0] != preview_name:
            os.rename(pngfiles[0], preview_name)
        assets['pngFile'] = preview_name
        with open(preview_name, 'rb') as png_file:
            png_reader = png.Reader(file=png_file)
            width, height, _, _ = png_reader.read()
            assets['pngWidth'] = str(width)
            assets['pngHeight'] = str(height)

    return assets


def build_one(infile, lily_path, do_preview, debug=False):
    """Primary entry point for the build entry point.

    :param debug: True of debugging.
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



def build(debug, database, infile, header_file):
    # The database name should be a name in the configuration file.
    # It would be difficult to make this a choice selection in the
    # argument parser so just check early and exit if necessary.
    if database not in CONFIG_DICT:
        puts(colored.red('Invalid database name - ' + database))
        return
    
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

    locator = mupub.LyLocator(header.get_value('lilypondVersion'))
    lily_path = locator.working_path()

    # Build each score, doing a preview on the first one only.
    do_preview = True
    for ly_file in infile:
        build_one(ly_file, lily_path, do_preview, debug)
        do_preview = False

    assets = collect_assets(infile[0])
    puts(colored.green('Creating RDF file'))
    header.writeRDF(os.path.basename(os.path.abspath('.'))+'.rdf', assets)


def main(args):
    """Module entry point for the build command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub build')
    parser.add_argument(
        '--debug',
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
        help='lilypond input file (try to work it out if not given)'
    )
    parser.add_argument(
        '--header-file',
        help='lilypond file that contains the header'
    )

    args = parser.parse_args(args)
    build(**vars(args))
