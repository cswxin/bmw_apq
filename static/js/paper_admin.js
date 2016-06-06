function submitpaper(paperid)
{
    $.post
    (
	"/submitpaper/",
	{paperid:paperid},
	function(msg)
	{
	    if (msg.result == 1)
	    {
		$("#submittip_"+paperid).html("提交成功，等待审核");
		$("#status_label_"+paperid).html(msg.status);
	    }
	    return false;
	},
	"json"
    )
}

function genreport(paperid)
{
    ret = confirm("确认生成单店报告？生成大约需要几秒钟的时间");
    if (ret)
    {
		$.post
		(
			"/genreport/",
			{paperid:paperid},
			function(msg)
			{
				if (msg.result == 1)
				{
					var html = "<a href=\"/file/"+ msg.purl + "\">下载</a>"
					$("#downloadreport_"+paperid).html(html);
					alert("报告生成！");
				}
				return false;
			},
			"json"
		)
    }
}

$(document).ready(function()
{
    $(".submitpaperlink").click(function(){
        var paperid = $(this).attr("paperid");
        submitpaper(paperid);
    })
    
    $(".genreport").click(function(){
        var paperid = $(this).attr("paperid");
        genreport(paperid);
    })
})
