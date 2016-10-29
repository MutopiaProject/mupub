"""Various mechanisms for validating a header.
"""

import abc
from mupub.header import REQUIRED_FIELDS
from clint.textui import colored, puts

class Validator(metaclass=abc.ABCMeta):
    """Abstract class that defines header validation protocols.
    """

    @abc.abstractmethod
    def validate_composer(self, composer):
        """Validate a composer"""
        return False

    @abc.abstractmethod
    def validate_style(self, style):
        """Validate a style"""
        return False

    @abc.abstractmethod
    def validate_license(self, license_name): # 'license' is a python builtin
        """Validate a license"""
        return False

    @classmethod
    def basic_checks(cls, header, verbose=False):
        """Perform basic checks on a header.

        Simple check to make sure that required fields are present.

        :param header: dict of header fields
        :returns: Number of failures discovered
        :rtype: int

        """

        failed_count = 0
        for required_field in REQUIRED_FIELDS:
            item = header.get_field(required_field)
            if not item:
                if verbose:
                    message = 'missing header keyword: {}'
                    puts(colored.red(message.format(required_field)))
                failed_count += 1

        # license check is done separately to accomodate for copyright
        # synonym.
        if header.get_field('copyright'):
            if verbose:
                puts(colored.yellow(('copyright will be updated to license')))
            header.set_field('license', header.get_field('copyright'))
        else:
            if not header.get_field('license'):
                if verbose:
                    puts(colored.red('no license or copyright found'))
                failed_count += 1

        return failed_count


    def validate_header(self, header, verbose=False):
        """Validate a header.

        If basic checks are good, several fields are checked against
        the database. The database check will make sure the references
        between tables will work correctly.

        :param header: dict of header fields
        :returns: True if required fields are present and have valid content.
        :rtype: bool

        """

        failures = self.basic_checks(header, verbose)
        if failures > 0:
            # No use bothering with further tests.
            return False
        if not self.validate_composer(header.get_field('composer')):
            if verbose:
                puts(colored.red('Invalid composer field: ' 
                                 + header.get_field('composer')))
            return False
        if not self.validate_style(header.get_field('style')):
            if verbose:
                puts(colored.red('Invalid style field: '
                                 + header.get_field('style')))
            return False
        if not self.validate_license(header.get_field('license')):
            if verbose:
                puts(colored.red('Invalid license field: '
                                 + header.get_field('license')))
            return False
        return True


class DBValidator(Validator):
    """Concrete class that defines a Validator that uses a database.
    """

    def __init__(self, connection):
        self.connection = connection

    def validate_composer(self, composer):
        """Validate a composer via a DB connection.

        :param composer: Mutopia composer key
        :returns: True if present in the database
        :rtype: bool

        """
        query = 'select count(*) from composers where composer=?;'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (composer,))
            (count,) = cursor.fetchone()
            return count == 1
        finally:
            cursor.close()
        return False


    def validate_style(self, style):
        """Validate a style via a DB connection.

        :param style: Style name
        :returns: True if this style name is in the database.
        :rtype: bool

        """
        query = 'select count(*) from styles where style=?'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (style,))
            (count,) = cursor.fetchone()
            return count == 1
        finally:
            cursor.close()
        return False


    def validate_license(self, license_name):
        """Validate a license via a DB connection.

        :param license_name: The name of the license.
        :returns: True if this license is in the database.
        :rtype: bool

        """
        query = 'select count(*) from licenses where license=?'
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (license_name,))
            (count,) = cursor.fetchone()
            return count == 1
        finally:
            cursor.close()
        return False
