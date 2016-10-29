"""
"""

__docformat__ = 'reStructuredText'

import glob
import gzip
import os
import png
import shutil
import zipfile
import mupub

def _collect_lyfile(basefnm):
    dir_name = basefnm + '-lys'
    if os.path.exists(dir_name):
        zip_name = dir_name+'.zip'
        with zipfile.ZipFile(zip_name, 'w') as lyzip:
            zip_list = mupub.utils.find_files(dir_name)
            for zip_entry in zip_list:
                lyzip.write(zip_entry)
        return zip_name
    else:
        return basefnm + '.ly'


def _zip_maybe(basefnm, tail, ziptail):
    files = glob.glob('*'+tail)
    if len(files) < 1:
        return 'empty'
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
        with zipfile.ZipFile(zip_name, 'w') as outzip:
            for file_to_zip in files:
                outzip.write(file_to_zip)
        for zipped_file in files:
            os.unlink(zipped_file)
        return zip_name


def collect_assets(basefnm):
    """After a build, collect all assets into their publishable components.

    Once the piece has been built by LilyPond, the assets are
    collected into other possible forms.

     - multiple LilyPond files are zipped together
     - multiple midi files are zipped
     - all PostScript files are zipped
     - multiple PDF files are zipped

    :param str basefnm: base filename used for asset naming.
    :returns: asset dictionary, useful for RDF creation.
    :rtype: dictionary containing name:value pairs of assets.

    """
    assets = {}
    assets['lyFile'] = _collect_lyfile(basefnm)
    assets['midFile'] = _zip_maybe(basefnm, '.mid', '-mids.zip')
    assets['psFileA4'] = _zip_maybe(basefnm, '-a4.ps', '-a4-pss.zip')
    assets['psFileLet'] = _zip_maybe(basefnm, '-let.ps', '-let-pss.zip')
    assets['pdfFileA4'] = _zip_maybe(basefnm, '-a4.pdf', '-a4-pdfs.zip')
    assets['pdfFileLet'] = _zip_maybe(basefnm, '-let.pdf', '-let-pdfs.zip')

    # process the preview image
    preview_name = basefnm + '-preview.png'
    if not os.path.exists(preview_name):
        pngfiles = glob.glob('*.preview.png')
        if len(pngfiles) > 0:
            # On multiple PNG files, use the first one
            os.rename(pngfiles[0], preview_name)
        else:
            raise mupub.IncompleteBuild('No preview image found.')

    assets['pngFile'] = preview_name
    with open(preview_name, 'rb') as png_file:
        png_reader = png.Reader(file=png_file)
        width, height, _, _ = png_reader.read()
        assets['pngWidth'] = str(width)
        assets['pngHeight'] = str(height)

    return assets