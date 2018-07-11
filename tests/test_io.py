import pkgutil
import gzip

import pytest

from edgePy.io import *  # A bad habit in practice, this tests `__all__`


# TestCommonFunctions
def test_get_open_function():
    file_name = "blah.gz"
    open_function, decode_required = get_open_function(filename=file_name)
    assert gzip.open == open_function
    assert decode_required is True

    file_name = "blah.txt"
    open_function, decode_required = get_open_function(filename=file_name)
    assert open == open_function
    assert decode_required is False


# Unit tests for ``edgePy.io.Importer``.
def test_init():
    filename = get_dataset_path('GSE49712_HTSeq.txt.gz')
    import_module = DataImporter(filename)

    assert 10 == len(import_module.samples)
    assert 21716 == len(import_module.raw_data)

    import_module.process_data()
    assert 10 == len(import_module.samples)
    assert 21716 == len(import_module.data)


def test_failure():
    with pytest.raises(Exception):
        DataImporter(None)


# TestGroupImporter.
def test_GroupImporter_init():
    filename = get_dataset_path('groups.txt')
    group_importer = GroupImporter(filename)

    assert 2 == len(group_importer.groups)
    assert 5 == len(group_importer.groups['Group 1'])
    assert 5 == len(group_importer.groups['Group 2'])
    assert "Group 1" == group_importer.samples['A_1']
    assert "Group 1" == group_importer.samples['A_3']
    assert "Group 1" == group_importer.samples['A_5']
    assert "Group 2" == group_importer.samples['B_2']
    assert "Group 2" == group_importer.samples['B_4']


def test_GroupImporter_failure():
    with pytest.raises(Exception):
        GroupImporter(None)


# Unit tests for packaged (optionally zipped during install) data.
def test_get_data_stream():
    """Tests finding packaged data with ``pkgutil.get_data()``"""
    pkgutil.get_data('edgePy', 'data/GSE49712_HTSeq.txt.gz')
