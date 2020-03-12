var murmur = '';
var current_page = 0;
var result_json = '';
var bottom_loading = false;

function catch_murmur()
{
    setTimeout(function ()
    {
        Fingerprint2.get(function (components)
        {
            var values = components.map(function (component) { return component.value })
            murmur = Fingerprint2.x64hash128(values.join(''), 31)
        })
    }, 500)
}

setTimeout("catch_murmur()", 50);

function onKeyDown(event)
{
     var e = event || window.event || arguments.callee.caller.arguments[0];
     if(e && e.keyCode==13)// enter 键
     {
        search();
     }
}

function search()
{
    clear();
    search_continue();
}

function search_continue()
{
    var keyword = $("#keyword").val();
    if(keyword == '')
        return;
    $.ajax({
        type: 'POST',
        url: 'search',
        data: {'murmur': murmur, 'keyword': keyword, 'page': current_page},
        dataType: 'json',
        success: function(res) {
            bottom_load_end();
            append_result(res.result_json)
        },
        error: function() {
            console.log('请求失败~');
        }
    });
}

function clear()
{
    current_page = 0;
    $("#p").html('');
}

function append_result(result_json)
{
    var _result = result_json == ""?{}:JSON.parse(result_json);
    var _rank = 1 + current_page * 10;
    var _html = "";
    for(var index in _result)
    {
        var item = _result[index];
        var _star = '暂无';
        var _desc = item["brief"];
        var _title = item["title"];
        var _date = item["date"];

        var dl = '<dl class="form-inline form-group">';
        dl += '<dt><a href="'+item['url']+'" target="_blank" style="font-size:18px"><b>';
        dl += _rank + '. '+ _title +'</b></a></dt>';
        dl += '<dd><p class="text-muted">* '+_desc+'</p><p class="text-muted">时间：'+_date+'　　评分：<span style="font-size:20px;height:16px;">'+_star+'</span></p></dd>';
        dl += '</dl>';
        dl += '<hr>';
        _html += dl;
        _rank += 1;
    }

    $("#p").append(_html);
}

function bottom_load()
{
    bottom_loading = true;
    $("#bottom_load").html('加载中...');
}

function bottom_load_end()
{
    bottom_loading = false;
    $("#bottom_load").html('');
}

$(window).scroll(function(){
　　var scrollTop = $(this).scrollTop();
　　var scrollHeight = $(document).height();
　　var windowHeight = $(this).height();
　　if(scrollTop + windowHeight == scrollHeight)
    {
        current_page += 1;
        bottom_load();
        search_continue();
　　}
});