
import pytest
from edgePy.data_import.mongodb.mongo_wrapper import MongoWrapper
from edgePy.data_import.mongodb.mongo_wrapper import MongoInserter
from edgePy.data_import.mongodb.mongo_wrapper import MongoUpdater


def test_mongo_wrapper_find_as_cursor(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    assert 'ensg_by_symbol' in mongodb.collection_names()
    cursor = mw.find_as_cursor('pytest', 'ensg_by_symbol', {}, {})

    count = 0
    for i in cursor:
        print(i)
        count += 1

    assert 3 == count


def test_mongo_wrapper_find_as_cursor_fail():
    mw = MongoWrapper('localhost', '27017')
    # do not set session to mongodb to cause this error.
    with pytest.raises(Exception):
        mw.find_as_cursor('pytest', 'fake_table', {'_id_': "something"}, {})


def test_mongo_wrapper_find_as_list(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    assert 'ensg_by_symbol' in mongodb.collection_names()
    value = mw.find_as_list('pytest', 'ensg_by_symbol', {}, {})
    assert value == [{'_id': 'BRCA1'}, {'_id': 'BRCA2'}, {'_id': 'TP53'}]


def test_mongo_wrapper_find_as_dict(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    assert 'ensg_by_symbol' in mongodb.collection_names()
    value = mw.find_as_dict('pytest', 'ensg_by_symbol', {})
    assert value == {'BRCA1': {'_id': 'BRCA1', 'ensgs': ['ENSG00000012048']},
                     'TP53': {'_id': 'TP53', 'ensgs': ['ENSG00000141510']},
                     'BRCA2': {'_id': 'BRCA2', 'ensgs': ['ENSG00000139618']}}


def test_mongo_wrapper_insert(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    mw.insert('pytest', 'test', [{'rec1': 'val1'}, {'rec2': 'val2'}])


def test_mongo_wrapper_create_index(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    mw.create_index('pytest', 'test', '_id')


def test_mongo_inserter_flush(mongodb):
    """This is not testable - the mongodb pytest module does not support bulk writes. """

    mi = MongoInserter('localhost', 27017, 'pytest', 'test')
    mi.session = mongodb
    # mi.add(['A', 'B', 'C'])
    mi.flush()

    pass


def test_mongo_inserter_add(mongodb):
    mi = MongoInserter('localhost', 27017, 'pytest', 'test')
    mi.session = mongodb
    mi.add(['A', 'B', 'C'])


def test_mongo_inserter_close(mongodb):
    mi = MongoInserter('localhost', 27017, 'pytest', 'test')
    mi.session = mongodb
    # mi.add(['A', 'B', 'C'])
    mi.close()


def test_mongo_inserter_create_index_key(mongodb):
    mi = MongoInserter('localhost', 27017, 'pytest', 'test')
    mi.session = mongodb
    mi.create_index('pytest', 'test', '_id')


def test_mongo_updater_flush(mongodb):
    """This is not testable - the mongodb pytest module does not support bulk writes. """
    mu = MongoUpdater('localhost', 27017, 'pytest', 'test')
    mu.session = mongodb
    mu.flush()


def test_mongo_updater_add(mongodb):
    mu = MongoUpdater('localhost', 27017, 'pytest', 'test')
    mu.session = mongodb
    mu.add({}, {'a': 'b'})


def test_mongo_updater_close(mongodb):
    mu = MongoUpdater('localhost', 27017, 'pytest', 'test')
    mu.session = mongodb
    mu.close()
