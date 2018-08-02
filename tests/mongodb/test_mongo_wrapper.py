

from src.data_import.mongodb.mongo_wrapper import MongoWrapper


def test_mongo_wrapper_find_as_cursor(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    assert 'ensg_by_symbol' in mongodb.collection_names()
    cursor = mw.find_as_cursor('pytest', 'ensg_by_symbol', {}, {})

    count = 0
    for i in cursor:
        print(i)
        count += 1

    assert 1 == count


def test_mongo_wrapper_find_as_list(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    assert 'ensg_by_symbol' in mongodb.collection_names()
    value = mw.find_as_list('pytest', 'ensg_by_symbol', {}, {})
    assert value == [{'_id': 'BRCA1'}]


def test_mongo_wrapper_find_as_dict(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    assert 'ensg_by_symbol' in mongodb.collection_names()
    value = mw.find_as_dict('pytest', 'ensg_by_symbol', {})
    assert value == {'BRCA1': {'_id': 'BRCA1', 'ensgs': ['ENSG00000012048']}}


def test_mongo_wrapper_insert(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    mw.insert('pytest', 'test', [{'rec1': 'val1'}, {'rec2': 'val2'}])


def test_mongo_wrapper_create_index(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    mw.create_index('pytest', 'test', '_id')


def test_mongo_inserter_flush(mongodb):
    pass


def test_mongo_inserter_add(mongodb):
    pass


def test_mongo_inserter_close(mongodb):
    pass


def test_mongo_inserter_create_index_key(mongodb):
    pass


def test_mongo_updater(mongodb):
    pass


def test_mongo_updater_flush(mongodb):
    pass


def test_mongo_updater_add(mongodb):
    pass


def test_mongo_updater_close(mongodb):
    pass
