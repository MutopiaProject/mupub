"""RDF processing module.

This is tailored for the MutopiaProject but has a few generic
mechanisms that can be applied to other projects using RDF.

"""

__docformat__ = 'reStructuredText'

import xml.etree.ElementTree as ET


RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
MP_NS = 'http://www.mutopiaproject.org/piece-data/0.1/'

# A simple class to simplify namespace usage.
# From effbot (Fredrik Lundh)
class NS:
    def __init__(self, uri):
        self.uri = '{'+uri+'}'
    def __getattr__(self, tag):
        return self.uri + tag
    def __call__(self, path):
        return "/".join(getattr(self, tag) for tag in path.split("/"))


# Convenient namespace definitions for this module
_MP = NS(MP_NS)
_RDF = NS(RDF_NS)

# This list sets the order for the RDF output. This is not strictly
# necessary --- RDF parsers really don't care about order --- but it
# is more human friendly to have a consistent order.
_MU_KEYS = ['title', 'composer', 'opus',
            'lyricist', 'for', 'date', 'style',
            'metre', 'arranger', 'source',
            'licence',
            'lyFile', 'midFile',
            'psFileA4', 'pdfFileA4',
            'psFileLet', 'pdfFileLet',
            'pngFile', 'pngHeight', 'pngWidth',
            'id',
            'maintainer', 'maintainerEmail', 'maintainerWeb',
            'moreInfo', 'lilypondVersion',
]


class MuRDF:
    def __init__(self):
        # Start an RDF document
        self.top = ET.Element(_RDF('RDF'))

        # The RDF document tree has a description as its sole element.
        self.description = ET.SubElement(self.top,
                                         _RDF('Description'),
                                         {_RDF('about'): '.'})
        # Generate the RDF with all elements in the order we want.
        # Ordering is mostly cosmetic but we still want to create a
        # blank-filled RDF of our expected elements.
        for key in _MU_KEYS:
            ET.SubElement(self.description, _MP(key))


    def update_description(self, name, value):
        """Update a description element in the RDF.

        This is an update not an insert so it expects to find `name`
        in the description of the RDF.

        :param str name: The name of an existing node in 
            description.
        :param str value: The new value of the named node.
        :returns: True if node is found and updated.
        :rtype: boolean

        """
        node = self.description.find(_MP(name))
        if node is None:
            return False
        node.text = value
        return True


    @classmethod
    def indent(cls, elem, level=0):
        """Indent xml tree in place.

        :param xml.etree.ElementTree elem: RDF to indent.
        :param int level: level for indent (recursive routine).

        """
        # also from effbot (Fredrik Lundh)

        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                cls.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


    def write_xml(self, path):
        """Write the ElementTree to RDF/XML.

        :param path: Name of output file.

        """
        # Registration of the namespace allows the output to define
        # xmlns attributes in the RDF header.
        ET.register_namespace('rdf', RDF_NS)
        ET.register_namespace('mp', MP_NS)
        MuRDF.indent(self.top)
        root = ET.ElementTree(element=self.top)
        with open(path, 'wb') as rdfout:
            root.write(rdfout, encoding='UTF-8', xml_declaration=True)
