"""Publishing module, implementing the build entry point.

This command is entered using the mupub command and may be as simple as, ::

  $ mupub build


"""

import argparse
import glob
import logging
import os
import sys
import shutil
import subprocess
from clint.textui import colored, puts
import mupub


def _remove_if_exists(path):
    if os.path.exists(path):
        os.unlink(path)


def _stripped_base(infile):
    basefnm = os.path.basename(infile)
    return basefnm[: basefnm.rfind(".")]


def _build_scores(base_params, infile):
    """Build scores in the required page sizes.

    :param base_params: List of LilyPond command and params.
    :param infile: The file to compile.

    """
    logger = logging.getLogger(__name__)

    pagedef = {"a4": "a4", "letter": "let"}
    build_params = [
        "--format=pdf",
        "--format=ps",
    ]
    basefnm = _stripped_base(infile)

    for psize in pagedef.keys():
        puts(colored.green("Building score, page size = " + psize))
        command = base_params + build_params
        command.append('-dpaper-size="{}"'.format(psize))
        command.append("--include=" + os.path.dirname(infile))
        command.append(infile)
        try:
            subprocess.check_output(command)
        except subprocess.CalledProcessError as cpe:
            logging.error("LilyPond returned an error code of %d" % cpe.returncode)
            return False

        # rename the pdf and ps files to include their page size
        pdf_fnm = basefnm + ".pdf"
        if os.path.exists(pdf_fnm):
            sized_pdf = basefnm + "-{0}.pdf".format(pagedef[psize])
            os.rename(pdf_fnm, sized_pdf)

        ps_fnm = basefnm + ".ps"
        if os.path.exists(ps_fnm):
            sized_ps = basefnm + "-{0}.ps".format(pagedef[psize])
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
    preview_fnm = mupub.CONFIG_DICT["common"].get("preview_fnm")
    if preview_fnm:
        tpath = os.path.join(os.path.dirname(infile), preview_fnm)
        if os.path.exists(tpath):
            logger.debug("Premade image found (%s) for preview" % tpath)
            # build a destination from the infile name
            namev = [
                os.path.basename(infile).rsplit(".")[0],
            ]
            namev.append(".preview")
            namev.append(tpath[tpath.rfind(".") :])  # extension
            dest = os.path.join("./", "".join(namev))
            _remove_if_exists(dest)
            shutil.copyfile(tpath, dest)
            logger.debug("Destination preview copied (%s)" % dest)
            return

    preview_params = [
        "-dno-include-book-title-preview",
    ]
    # 2.12 doesn't understand the --preview flag
    if lpversion < mupub.LyVersion("2.12"):
        preview_params.append("-dresolution=101"),
        preview_params.append("--preview")
        preview_params.append("--no-print")
        preview_params.append("--format=png")
    else:
        # 2.12 doesn't have the svg backend.
        # It may be easier to tweak things here rather than explore
        # all possibilities.
        if lpversion < mupub.LyVersion("2.14"):
            force_png_preview = True
        preview_params.append("--include=" + os.path.dirname(infile))
        preview_params.append("-dno-print-pages"),
        preview_params.append("-dpreview")
        if force_png_preview:
            preview_params.append("--format=png")
        else:
            preview_params.append("-dbackend=svg")

    command = base_params + preview_params
    command.append(infile)
    puts(colored.green("Building preview and midi files"))
    try:
        subprocess.check_output(command)
    except subprocess.CalledProcessError as cpe:
        logging.error("LilyPond returned an error code of %d" % cpe.returncode)
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
        puts(colored.red("Failed to resolve infile %s" % infile))
        return False

    base_params = [
        lily_path,
        "-dno-point-and-click",
    ]
    if not _build_scores(base_params, infile):
        return False
    if do_preview:
        return _build_preview(base_params, lpversion, infile, force_png_preview)
    return True


def _lily_build(infile, header, force_png_preview=False, skip_preview=False):
    lpversion = mupub.LyVersion(header.get_value("lilypondVersion"))
    locator = mupub.LyLocator(str(lpversion), progress_bar=True)
    lily_path = locator.working_path()
    if not lily_path:
        # No compiler (too old?) installed for this revision.
        sys.exit(-2)

    # Build each score, doing a preview on the first one only (unless skipping)
    do_preview = not skip_preview
    count = 0
    for ly_file in infile:
        count += 1
        puts(
            colored.green(
                "Processing LilyPond file {} of {}".format(count, len(infile))
            )
        )
        _build_one(ly_file, lily_path, lpversion, do_preview, force_png_preview)
        do_preview = False


def build(
    infile,
    header_file,
    parts_folder,
    collect_only=False,
    skip_header_check=False,
    force_png_preview=False,
):
    """Build one or more |LilyPond| files, generate publication assets.

    :param infile: The |LilyPond| file(s) to build.
    :param header_file: The file containing the header information.
    :param parts_folder: Build part scores contained in this folder.
    :param collect_only: Skip building, just collect assets and build RDF.
    :param skip_header_check: Skip header validation.
    :param force_png_preview: Coerce PNG format in preview

    This command presumes your current working directory is the
    location where the contributed source files live in the
    MutopiaProject hierarchy. A successful build will create all
    necessary assets for publication.

    """
    logger = logging.getLogger(__name__)
    logger.info("build command starting")
    base, lyfile = mupub.utils.resolve_input()

    if not mupub.commands.init.verify_init():
        return

    if len(infile) < 1:
        if lyfile:
            infile.append(lyfile)
        else:
            logger.error("Failed to resolve any input files.")
            logger.info("Make sure your working directory is correct.")
            return

    # if a header file was given, use that for reading the header,
    # else infile.
    if header_file:
        header_file = mupub.resolve_lysfile(header_file)
        header = mupub.find_header(header_file)
    else:
        header = mupub.find_header(infile[0])

    if not header:
        puts(colored.red("failed to find header"))
        return

    # Try to handle missing required fields.
    if not header.is_valid():
        mfields = header.missing_fields()
        if len(mfields) > 0:
            logger.warning("Invalid header, missing: %s" % mfields)
        if skip_header_check:
            puts(colored.yellow("Header not complete, continuing."))
        else:
            # return without building otherwise
            puts(colored.red("Header validation failed."))
            logger.debug("Incorrect or incomplete header.")
            return

    # The user can opt to build manually and then use this application
    # to collect all the publication assets.
    if not collect_only:
        # build infile collection first
        _lily_build(infile, header, force_png_preview)

        # Build all parts if requested.
        if parts_folder:
            # User may fully specify the folder name
            parts_path = parts_folder
            if not os.path.exists(parts_path):
                # ... or we'll try to find it here
                parts_path = os.path.join(base + "-lys", parts_folder)
                if not os.path.exists(parts_path):
                    puts(
                        colored.red(
                            "Failed to find parts folder - {}".format(parts_folder)
                        )
                    )
                    puts(colored.red("Skipping asset collection"))
                    return
            parts_list = []
            for fnm in os.listdir(path=parts_path):
                if fnm.endswith(".ly"):
                    parts_list.append(os.path.join(parts_path, fnm))
            if len(parts_list) > 0:
                puts(colored.green("Found {} part scores".format(len(parts_list))))
                _lily_build(parts_list, header, False, True)

    # rename all .midi files to .mid
    for mid in glob.glob("*.midi"):
        os.rename(mid, mid[: len(mid) - 1])

    try:
        assets = mupub.collect_assets(base)
        puts(colored.green("Creating RDF file"))
        header.write_rdf(base + ".rdf", assets)

        # remove by-products of build
        _remove_if_exists(base + ".ps")
        _remove_if_exists(base + ".png")
        _remove_if_exists(base + ".preview.png")
        _remove_if_exists(base + ".preview.svg")
        _remove_if_exists(base + ".preview.eps")
        logger.info("Publishing build complete.")
    except mupub.IncompleteBuild as exc:
        logger.warning(exc)
        puts(colored.red("Rebuild needed, assets were not completely built."))
        puts(colored.red('Do a "mupub clean" before next build.'))


def main(args):
    """Module entry point for the build command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog="mupub build")
    parser.add_argument(
        "infile",
        nargs="*",
        default=[],
        help="LilyPond input file (try to work it out if not given)",
    )
    parser.add_argument("--header-file", help="LilyPond file that contains the header")
    parser.add_argument("--parts-folder", help="Specify folder containing part scores")
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Collect built files into publishable assets",
    )
    parser.add_argument(
        "--skip-header-check",
        action="store_true",
        help="Do not exit on failed header validation",
    )
    parser.add_argument(
        "--force-png-preview",
        action="store_true",
        help="Force a preview with PNG format instead of default SVG",
    )

    args = parser.parse_args(args)
    build(**vars(args))
