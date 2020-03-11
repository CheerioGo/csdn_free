var murmur = '';
var current_page = 0;
var result_json = '';

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
    current_page = 0;
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
            append_result(res.result_json)
        },
        error: function() {
            console.log('请求失败~');
        }
    });
}

function clear()
{
    $("#p").html('');
}

function append_result(result_json)
{
    for(var _url in result_json)
    {
        var stars_array = ["☆☆☆☆☆","★☆☆☆☆","★★☆☆☆","★★★☆☆","★★★★☆","★★★★★"];
        var _star = stars_array[_result[_url]["stars"]];
        var _desc = _result[_url]["description"];
        var _title = _result[_url]["title"];
        var _date = _result[_url]["upload_date"];

        var dl = '<dl class="form-inline form-group">';
        dl += '<dt><a href="'+_url+'" target="_blank" style="font-size:18px"><b>';
        dl += _rank + '. '+ _title +'</b></a></dt>';
        dl += '<dd><p class="text-muted">* '+_desc+'</p><p class="text-muted">时间：'+_date+'　　评分：<span style="font-size:20px;height:16px;">'+_star+'</span></p></dd>';
        dl += '</dl>';
        dl += '<hr>';
        _html += dl;
        _rank += 1;
    }

    $("#p").append(_html);
}