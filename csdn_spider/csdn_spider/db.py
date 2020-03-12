import pymongo
import pymongo.errors
from csdn_spider import db_setting

db: pymongo.MongoClient = None
raw: pymongo.collection.Collection = None
user: pymongo.collection.Collection = None
zero: pymongo.collection.Collection = None


# state 说明
# user - 0 : 初始资源
# user - 1 : 已爬取关注列表
# user - 2 : 已爬取资源列表
# zero - 0 : 初始资源
# zero - 1 : 已下载至本地资源
# zero - 2 : 已上传至云端资源

def __init_db():
    client = pymongo.MongoClient(host=db_setting.host, port=db_setting.port
                                 , username=db_setting.username, password=db_setting.password)
    global db
    global user
    global zero
    db = client['csdn']

    collections = db.list_collection_names()
    if 'user' not in collections:
        db['user'].create_index([('id', 1)], unique=True)
        db['user'].create_index([('state', 1)])
        db['user'].create_index([('zero', 1)])
    if 'zero' not in collections:
        db['zero'].create_index([('id', 1)], unique=True)
        db['zero'].create_index([('state', 1)])

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
    try:
        zero.insert_one(docs)
    except pymongo.errors.DuplicateKeyError:
        return False
    return True


def zero_exist(_id):
    __get_db()
    return zero.find_one({'id': _id}) is not None


def zero_get_state_url():
    __get_db()
    data = zero.find_one({'state': 0})
    if data is None:
        return None
    zero_set_state(data['id'], 1)
    return data['url']


def zero_set_state(_id, state):
    __get_db()
    zero.update_one({'id': _id}, {'$set': {'state': state}})


# user
def user_get_state_id():
    __get_db()
    data = user.find_one({'state': 0})
    if data is None:
        return None
    _id = data['id']
    user_set_state(_id, 1)
    return _id


def user_get_zero_id():
    __get_db()
    data = user.find_one({'zero': 0})
    if data is None:
        return None
    _id = data['id']
    user_set_zero(_id, 1)
    return _id


def user_insert(docs):
    __get_db()
    try:
        user.insert_one(docs)
    except pymongo.errors.DuplicateKeyError:
        return False
    return True


def user_set_state(_id, state):
    __get_db()
    user.update_one({'id': _id}, {'$set': {'state': state}})


def user_set_zero(_id, zero):
    __get_db()
    user.update_one({'id': _id}, {'$set': {'zero': zero}})


def user_exist(_id):
    __get_db()
    return user.find_one({'id': _id}) is not None


def user_count():
    __get_db()
    return user.count()
