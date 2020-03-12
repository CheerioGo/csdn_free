from django.shortcuts import render
from django.http import HttpResponse
from res_search import db
import json
import jieba.analyse


def _response(result_json=''):
    return HttpResponse(
        json.dumps({'result_json': result_json}),
        content_type='application/json')


def index(request):
    return render(request, 'index.html')


def search(request):
    if request.method == 'GET':
        return HttpResponse()

    uuid = request.POST.get('murmur', '')
    keyword = request.POST.get('keyword', '')
    page = int(request.POST.get('page', '0'))
    if uuid == '':
        return _response('none')

    keywords = jieba.analyse.extract_tags(keyword, 3)
    result = db.zero_search(keywords, 10, page * 10)
    result_json = json.dumps(result)
    return _response(result_json)


def log(uuid, msg):
    import datetime
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
    print('[{}]：{} 于 ({})'.format(uuid[0:6], msg, now_time))
