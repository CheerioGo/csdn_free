import pymongo

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
    client = pymongo.MongoClient(host="127.0.0.1", port=27017)
    global db
    global user
    global zero
    db = client['csdn']

    collections = db.list_collection_names()
    if 'user' not in collections:
        db['user'].create_index([('id', 1)], unique=True)
        db['user'].create_index([('state', 1)], unique=False)
    if 'zero' not in collections:
        db['zero'].create_index([('id', 1)], unique=True)
        db['zero'].create_index([('state', 1)], unique=False)

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
def user_get_id(state):
    __get_db()
    data = user.find_one({'state': state})
    if data is None:
        return None
    _id = data['id']
    user_set_state(_id, state + 1)
    return _id


def user_insert(docs):
    __get_db()
    user.insert_one(docs)


def user_set_state(_id, state):
    __get_db()
    user.update_one({'id': _id}, {'$set': {'state': state}})


def user_exist(_id):
    __get_db()
    return user.find_one({'id': _id}) is not None
