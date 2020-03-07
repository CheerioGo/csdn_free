import pymongo

db: pymongo.MongoClient = None
raw: pymongo.collection.Collection = None
user: pymongo.collection.Collection = None
zero: pymongo.collection.Collection = None


def __init_db():
    client = pymongo.MongoClient(host="127.0.0.1", port=27017)
    global db
    global raw
    global user
    global zero
    db = client['csdn']

    collections = db.list_collection_names()
    if 'raw' not in collections:
        db['raw'].create_index([('url', 1)], unique=True)
    if 'user' not in collections:
        db['user'].create_index([('id', 1)], unique=True)
    if 'zero' not in collections:
        db['zero'].create_index([('id', 1)], unique=True)

    raw = db['raw']
    user = db['user']
    zero = db['zero']
    return db


def __get_db():
    global db
    if db is None:
        __init_db()
    return db


# zero
def zero_exist(_id):
    __get_db()
    return zero.find_one({'id': _id}) is not None


def zero_get_one(_id):
    __get_db()
    return zero.find_one({'download', False})


def zero_downloaded(_id):
    __get_db()
    zero.update_one({'id': _id}, {'download', True})
