
from nose.tools import eq_, assert_raises

from unittest import TestCase

from edgePy.edgePy import parse_arguments

class TestEdgePy(TestCase):
    """Unit tests for ``edgePy.io.Importer``"""

    def test_parse_argumants(self):
        text_file = "file.txt"
        groups_file = "groups.txt"
        args = parse_arguments(['--count_file', text_file, "--groups_file", groups_file])
        eq_(text_file, args.count_file)
        eq_(groups_file, args.groups_file)

