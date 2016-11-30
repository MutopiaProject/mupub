"""tagedit module, routines for editing tags in a LilyPond header
"""
from datetime import date
import re
import mupub

_HEADER_PAT = re.compile(r'\\header')
_HTAG_PAT = re.compile(r'^(\W*)(\w+)\s*=\s*\"(.*)\"')
_MU_TAGS = ['footer', 'copyright', 'tagline']

def _net_braces(line):
    return line.count('{') - line.count('}')


def _augmented_table(table, muid):
    tagtable = dict()

    # Figure out the proper mutopia id. The default is what the user
    # specified on the command line.
    mu_id = muid
    if 'footer' in table:
        _,mu_id = mupub.core.id_from_footer(table['footer'])

    # Any header editing at this point, existing or new contribution,
    # will get today's date.
    today = date.today().strftime('%Y/%m/%d')
    tagtable['footer'] = '"Mutopia-{0}-{1}"'.format(today,mu_id)
    tagtable['copyright'] = '"the new copyright text"'
    tagtable['tagline'] = '##f'

    return tagtable


def tag_header(infile, outfile, htable, muid):
    net_braces = 0
    header_started = False
    header_done = False
    found_headers = []
    new_tags = []

    if 'license' not in htable:
        # an old header, assign the license tag to the copyright
        htable['license'] = '"{0}"'.format(htable['copyright'])
        new_tags.append('license')

    htable.update(_augmented_table(htable, muid))
    lines = infile.readlines()
    indent = '  '
    for infline in lines:
        if header_done:
            outfile.write(infline)
            continue

        # attempt to discard comments
        line = infline.split('%', 1)[0]

        # search for start of header
        if not header_started:
            if _HEADER_PAT.search(line):
                header_started = True
                net_braces += _net_braces(line)
            outfile.write(infline)
            continue

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
                header_done = True
                for tag in new_tags:
                    outfile.write(indent)
                    outfile.write('{0} = {1}\n'.format(tag, htable[tag]))
                for tag in _MU_TAGS:
                    outfile.write(indent)
                    outfile.write('{0} = {1}\n'.format(tag, htable[tag]))
                outfile.write(infline)

    return htable
