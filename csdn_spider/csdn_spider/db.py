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
def zero_insert(docs):
    __get_db()
    zero.insert_one(docs)


def zero_exist(_id):
    __get_db()
    return zero.find_one({'id': _id}) is not None


# user
def user_get_crawl_id():
    __get_db()
    data = user.find_one({'crawl': False})
    if data is None:
        return None
    _id = data['id']
    user_crawled(_id)
    return _id


def user_insert(_id):
    __get_db()
    user.insert_one({'id': _id, 'crawl': False})


def user_crawled(_id):
    __get_db()
    user.update_one({'id': _id}, {'$set': {'crawl': True}})


def user_exist(_id):
    __get_db()
    return user.find_one({'id': _id}) is not None


# raw
def raw_get_crawl_url():
    __get_db()
    data = raw.find_one({'crawl': False})
    if data is None:
        return None
    _url = data['url']
    raw_crawled(_url)
    return _url


def raw_insert(url):
    __get_db()
    raw.insert_one({'url': url, 'crawl': False})


def raw_crawled(url):
    __get_db()
    raw.update_one({'url': url}, {'$set': {'crawl': True}})


def raw_exist(url):
    __get_db()
    return raw.find_one({'url': url}) is not None
