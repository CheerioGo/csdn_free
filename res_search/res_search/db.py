import pymongo
import bson
import datetime
import time

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
    client = pymongo.MongoClient(host="39.105.150.229", port=8743, username="yinlong91", password="yl873044")
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
    zero.insert_one(docs)


def zero_exist(_id):
    __get_db()
    return zero.find_one({'id': _id}) is not None


def build_query(keywords, op, tag):
    query = {f'${op}': []}
    for k in keywords:
        k = k.strip('/i')
        k = k.strip('/')
        query[f'${op}'].append({f'{tag}': {'$regex': f'{k}', '$options': '$i'}})
    return query


def to_json_dict(d):
    dd = {}
    for k in d:
        o = d[k]
        if isinstance(o, bson.ObjectId):
            continue
        if isinstance(o, datetime.datetime):
            dd[k] = datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        dd[k] = o
    return dd


def build_result(*args, ):
    result = []
    for r in args:
        for ri in r:
            jdict = to_json_dict(ri)
            if len(jdict['brief']) > 200:
                jdict['brief'] = jdict['brief'][:200] + '...'
            result.append(jdict)
    return result


def print_log(keywords, count, step, st):
    print(f'search keys: {keywords}, count: {count}, cost: {time.time() - st:.2f}s, step: {step}')


def zero_search(keywords, limit, skip):
    __get_db()
    __st = time.time()
    r1 = zero.find(build_query(keywords, 'and', 'title')).skip(skip).limit(limit)
    raw_count = r1.count()
    count = r1.count(with_limit_and_skip=True)
    print_log(keywords, count, 1, __st)
    if count >= limit:
        return build_result(r1)

    __st = time.time()
    _skip = max(skip - raw_count, 0)
    r2 = zero.find(build_query(keywords, 'and', 'brief')).skip(_skip).limit(limit - count)
    raw_count += r2.count()
    count += r2.count(with_limit_and_skip=True)
    print_log(keywords, count, 2, __st)
    if count >= limit:
        return build_result(r1, r2)

    __st = time.time()
    _skip = max(skip - raw_count, 0)
    r3 = zero.find(build_query(keywords, 'or', 'title')).skip(_skip).limit(limit - count)
    raw_count += r3.count()
    count += r3.count(with_limit_and_skip=True)
    print_log(keywords, count, 3, __st)
    return build_result(r1, r2, r3)

