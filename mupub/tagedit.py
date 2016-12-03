# -*- coding: utf-8 -*-
"""tagedit module, routines for editing tags in a LilyPond header
"""

from datetime import date
import logging
import os
import re
from string import Template
import tempfile
import mupub

_HEADER_PAT = re.compile(r'\\header')
_HTAG_PAT = re.compile(r'^(\W*)(\w+)\s*=\s*\"(.*)\"')
_MU_TAGS = ['footer', 'copyright', 'tagline']

# All public domain licenses get this format:
_PD_SUBS_FMT = """\"Placed in the \" \
\\with-url {0} \"Public Domain\" \
\" by the typesetter \"\
"""

# LilyURL is a simple holder of copyright information that will be
# used in a header's copyright line.
class LilyURL():
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.is_pd = False
        if 'Public' in name:
            self.is_pd = True

    def __str__(self):
        """Output that was useful during debugging, may be removed."""
        return '{0} - {1}'.format(self.name, self.is_pd)


    def get_url(self):
        """Retrieve the copyright as LilyPond markup.

        :returns: An string appropriate for the copyright tag.
        :rtype: str

        """
        if self.is_pd:
            return _PD_SUBS_FMT.format(self.url)
        else:
            return "\\with-url {0} {1}".format(self.url, self.name)


    def get_timestamp(self, year):
        """Retrieve an appropriate timestamp. For public domain this
        will be an empty string.
        """
        if self.is_pd:
            return ""
        return '©\" {0} \"'.format(year)


# Make a license dictionary for their corresponding url definition
# structures.
_LICENSES = {
    'Public Domain': LilyURL(
        '#"http://creativecommons.org/licenses/publicdomain"',
        'public domain'),
    'Creative Commons Attribution 3.0': LilyURL(
        '#"http://creativecommons.org/licenses/by/3.0"',
        '"Creative Commons Attribution 3.0 (Unported) License"'),
    'Creative Commons Attribution-ShareAlike 3.0': LilyURL(
        '#"http://creativecommons.org/licenses/by-sa/3.0/"',
        '"Creative Commons Attribution ShareAlike 3.0 (Unported) License"'),
    'Creative Commons Attribution 4.0': LilyURL(
        '#"http://creativecommons.org/licenses/by/4.0/"',
        '"Creative Commons Attribution 4.0 International License"'),
    'Creative Commons Attribution-ShareAlike 4.0': LilyURL(
        '#"http://creativecommons.org/licenses/by-sa/4.0/"',
        '"Creative Commons Attribution ShareAlike 4.0 International License"'),
    'Creative Commons Public Domain Dedication 1.0': LilyURL(
        '#"http://creativecommons.org/publicdomain/zero/1.0/"',
        ' "Creative Commons Public Domain Dedication 1.0 (CC0 Universal)"'),
    'Creative Commons Public Domain Mark 1.0': LilyURL(
        '#"http://creativecommons.org/publicdomain/mark/1.0/"',
        '"Creative Commons Public Domain Mark 1.0"'),
}


# Define a template for text processing the copyright. This targets
# the python standard Template module for processing --- note the
# embedded tags, $TIMESTAMP and $LICENSE_URL. Before handing off to
# the template engine this array of strings has its leading spaces
# trimmed and then joined together in one long line.
#
# Pay careful attention to edits here --- the onl way to test the
# output is to process lilypond files into PDFs and review.
#
_CC_TEMPLATE = [
    "\\markup {",
    "  \\override #'(font-name . \"DejaVu Sans, Bold\") ",
    "  \\override #'(baseline-skip . 0) ",
    "  \\right-column {",
    "  \\with-url #\"http://www.MutopiaProject.org\" {",
    "    \\abs-fontsize #9  \"Mutopia \" \\concat {",
    "      \\abs-fontsize #12 \\with-color #white \"ǀ\" ",
    "      \\abs-fontsize #9 \"Project \"",
    "      }",
    "    }",
    "  }",
    "  \\override #'(font-name . \"DejaVu Sans, Bold\") ",
    "  \\override #'(baseline-skip . 0 ) ",
    "  \\center-column {",
    "    \\abs-fontsize #11.9 \\with-color #grey \\bold {",
    "    \"ǀ\" \"ǀ\"",
    "    }",
    "  }",
    "  \\override #'(font-name . \"DejaVu Sans,sans-serif\") ",
    "  \\override #'(baseline-skip . 0) ",
    "  \\column { \\abs-fontsize #8 \\concat {",
    "    \"Typeset using \" ",
    "    \\with-url #\"http://www.lilypond.org\" \"LilyPond \" ",
    "    $TIMESTAMP",
    "    \"by \" \\maintainer \" — \" \\footer}",
    "    \\concat {",
    "      \\concat {",
    "        \\abs-fontsize #8 { ",
    "        $LICENSE_URL ",
    "         \" — free to distribute, modify, and perform\" ",
    "        }",
    "      }",
    "      \\abs-fontsize #13 \\with-color #white \"ǀ\" ",
    "    }",
    "  }",
    "}",
]


def get_copyright(cc_name, date):
    """Retrieve a copyright definition.

    :param str cc_name: The name of the copyright. It must match a
                 dictionary key in _LICENSES.
    :param date: The date for the copyright, typically from the
                 mutopia identifier (footer) string
    :returns: A complete copyright for insertion into a LilyPond header.
    :rtype: string

    """
    if cc_name not in _LICENSES:
        # ... probably need to raise an exception here ...
        return '"no copyright available."'

    lic = _LICENSES[cc_name]
    template = Template(''.join([x.lstrip() for x in _CC_TEMPLATE]))
    return template.substitute(TIMESTAMP=lic.get_timestamp(date.year),
                               LICENSE_URL=lic.get_url())


"""
Tag editing section.
"""

# A simple brace counter for header parsing
def _net_braces(line):
    return line.count('{') - line.count('}')


def _augmented_table(table, muid):
    """Return a table of mutopia-specific elements from the header.

    :param table: The header key:value pairs.
    :param muid: The mutopia id (from the footer)
    :returns: A table of extra header definitions for publishing.
    :rtype: dict

    """
    tagtable = dict()

    # Figure out the proper mutopia id. The default is what the user
    # specified on the command line.
    mu_id = muid
    if 'footer' in table:
        pubdate,mu_id = mupub.core.id_from_footer(table['footer'])
    else:
        pubdate = date.today()

    # Any header editing at this point, existing or new contribution,
    # will get today's date.
    today = date.today().strftime('%Y/%m/%d')
    tagtable['footer'] = '"Mutopia-{0}-{1}"'.format(today,mu_id)
    tagtable['copyright'] = get_copyright(table['license'], pubdate)
    tagtable['tagline'] = '##f'

    return tagtable


def tag_header(infile, outfile, htable, muid):
    """Tag the outfile with mutopia publishing elements from infile

    :param File infile: The input file.
    :param File outfile: The output file.
    :param htable: The header key:value pairs from the input file.
    :param muid: The mutopia integer identifier.
    :returns: The htable passed on input.
    :rtype: dict

    """
    net_braces = 0
    header_started = False
    header_done = False
    found_headers = []
    new_tags = []

    # Provide for older headers that use copyright instead of license.
    if 'license' not in htable:
        # an old header, assign the license tag to the copyright
        htable['license'] = '\"{0}\"'.format(htable['copyright'])
        new_tags.append('license')

    htable.update(_augmented_table(htable, muid))
    lines = infile.readlines()
    indent = '  '
    for infline in lines:
        if header_done:
            outfile.write(infline)
            continue            # writing in to out after header

        # Attempt to discard comments
        line = infline.split('%', 1)[0]
        if len(line.strip()) < 1:
            outfile.write(infline)
            continue

        # Search for start of header
        if not header_started:
            if _HEADER_PAT.search(line):
                header_started = True
                net_braces += _net_braces(line)
            outfile.write(infline)
            continue            # until found

        # - - - here once the header has started - - -

        hmatch = _HTAG_PAT.match(line)
        if hmatch:
            tag = hmatch.group(2)
            # Defer all "our" tag writing until the end of the header.
            if tag not in _MU_TAGS:
                outfile.write(infline)
                indent = hmatch.group(1)
        else:
            net_braces += _net_braces(line)
            if net_braces < 1:
                # Mark us done so that on next loop we just copy the
                # remainder of input file to output.
                header_done = True

                # Write new tags and all the augmented tags that also
                # have a match in _MU_TAGS.
                for tag in new_tags:
                    outfile.write(indent)
                    outfile.write('{0} = {1}\n'.format(tag, htable[tag]))
                for tag in _MU_TAGS:
                    outfile.write(indent)
                    outfile.write('{0} = {1}\n'.format(tag, htable[tag]))
                # infline contains the closing brace that got us here.
                outfile.write(infline)

    return htable


def tag_file(header_file, id):
    """Tag the given header file.

    The tagging process happens in this sequence:

      - obtain the header table from the file
      - read the file, tagging and writing to a temporary file
      - on success, rename the input file to a backup and copy the
        temporary file into its place.

    :param str header_file: input LilyPond file name
    :param int id: The mutopia identifier
    """
    htable = mupub.LYLoader().load(header_file)
    if not htable:
        logger.info('No header found for %s.', header_file)
        return

    # Create and write the temporary tagged file.
    with tempfile.NamedTemporaryFile(mode='w',
                                     suffix='.ly',
                                     prefix='mu_',
                                     delete=False) as outfile:
        outfnm = outfile.name
        with open(header_file, mode='r', encoding='utf-8') as infile:
            mupub.tag_header(infile, outfile, htable, id)

    if os.path.exists(outfnm):
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
    else:
        # Unlikely to get here --- if this doesn't exist an exception
        # should have been raised --- but just in case.
        logger = logging.getLogger(__name__)
        logger.error('Something went wrong processing %s' % header_file)
