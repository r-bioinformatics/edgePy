

def test_ImportFromMongodb(mongodb):
    assert 'ensg_by_symbol' in mongodb.collection_names()
