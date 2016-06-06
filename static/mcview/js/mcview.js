function form_onsubmit(obj)
{
	ValidationPassed = true;
	password=obj.password.value;
	if(obj.username.value=="")
	{
		alert("请输入您的用户名！\n");
		ValidationPassed = false;
		obj.username.focus();
		return false;
	}

	if(obj.password.value=="" && ValidationPassed)
	{
		alert("请输入您的密码！\n");
		ValidationPassed = false;
		obj.password.focus();
		return false;
	}

	if(obj.VerifyCode.value=="" && ValidationPassed)
	{
		alert("请输入验证码！\n");
		ValidationPassed = false;
		obj.VerifyCode.focus();
	}

	if(ValidationPassed){
		obj.submit();
	}
}
function reaLength(strVal)
	{
		var tempStr ;
		tempStr = strVal.replace(/(^\s*)|(\s*$)/g, '');
		
		return tempStr.replace(/[^\x00-\xff]/g,"**").length;
	}

function enter_submit(event) {
    if(event.keyCode==13){
        $("#loginbutton").click();
	}
}

function changepwd_enter_submit(event){
    if(event.keyCode==13){
        $(".in").click();
	}
}

function Juge(theForm)
{
oldpassword=theForm.oldpassword.value;
password=theForm.password.value;
confirmpass=theForm.confirmpass.value;
if(oldpassword== "")
    {
     alert("请输入旧密码！");
     theForm.oldpassword.focus();
     return (false);
    }
if(password== "")
    {
     alert("请输入新密码！");
     theForm.password.focus();
     return (false);
    }
if (password.indexOf("'")>0)
    {
    alert("新密码含有非法字符，请重试！！"); 
    theForm.password.focus();
    return false; 
    }
if(confirmpass== "")
    {
     alert("请输入确认密码！");
     theForm.confirmpass.focus();
     return (false);
    }    
if (confirmpass!=password)
    {
    alert("两次输入的密码不相同，请重试！"); 
    theForm.password.focus();
    return false; 
    }
}

function preloadImg(url){
	var img = new Image();
	img.src = url;
}

function changeimg(){
	preloadImg("/static/mcview/images/east.jpg");
	preloadImg("/static/mcview/images/north.jpg");
	preloadImg("/static/mcview/images/south.jpg");
	preloadImg("/static/mcview/images/west.jpg");
	$(".area").hover(function(){
		var regional = $(this).attr('alt');
		var url = "/static/mcview/images/"+regional+".jpg";
		$("#map").attr("src",url);
	},function (){});

}
function makeoption(select,data){
	var opt = select.children();
	opt.filter('option[value!=""]').remove();
	var add_opt = [];
	for (var i=0;i<data.length;i++){
		add_opt.push('<option value="'+data[i][0]+'">'+data[i][1]+'</option>');
	}
	var a_opt = add_opt.join('\n');
	select.append(a_opt);
}

function getdata(type,value){
	if (value == ""){
		return false;
	}
	switch(type){
		case "city":
			var select = $('#mycity .select01');
			break
		case "dealer":
			var select = $('#mydealer .select01');
			break
		default:
			return false;
	}
	$.ajax({
		type:"POST",
		url:"/ajaxgetoption/",     
		data:{type:type,value:value},
		dataType:"json",
		error: function (XMLHttpRequest){
			alert(XMLHttpRequest.responseText);
			return false;
		},
		success: function (data){
			makeoption(select,data);
		}
	});
}

function AddDealer(){
	var dealer_id = $('#mydealer .select01').val();
	var compare_dealers = $('.compare_dealer');
	if (compare_dealers.length>20)
	{
		alert("至多只能选择20家经销商进行对比！\n");
		return false;
	}
	if (dealer_id=="")
	{
		alert("请选择经销商！\n");
		return false;
	}
	if($('#compare_'+dealer_id)[0])
	{
		alert("所选经销商已经存在！\n");
		return false;
	}
	var id = compare_dealers.length +1
	$.ajax({
		type:"POST",
		url:"/ajaxgetdealerinfoforcompare/",
		data:{dealer_id:dealer_id},
		dataType:"json",
		error: function (XMLHttpRequest){
			alert(XMLHttpRequest.responseText);
			return false;
		},
		success: function (data){
			if (data.status == 0){
				status_cn = '未执行访问';
				status_en = 'Hasn’t been visited';
			}
			else if (data.status == 1){
				status_cn = '报告未生成';
				status_en = 'Report not available now ';
			}
			else if (data.status >= 2){
				status_cn = '报告已生成';
				status_en = 'Report finished';
			}
			var html = '<tr id="compare_'+dealer_id+'" class="compare_dealer" name="'+dealer_id+'"><td width="8%"><strong>'+id+'</strong></td>'+
				'<td width="13%"><strong>'+data.city_cn+'</strong><br>'+data.city_en+'</td><td width="12%"><strong>'+data.province_cn+'</strong><br>'+data.province_en+'</td>'+
				'<td width="43%"><strong>'+data.name_cn+'</strong><br>'+data.name_en+'</td>'+
				'<td width="24%"><strong>'+status_cn+'</strong><br>'+status_en+'</td></tr>';
			$('#DivCompDealer tbody').append(html);
		}
	});
}

// function top(){
	// $('html,body').animate({scrollTop: 0}, 1000);
// }

function CompDealer(){
	var comparedealer = $('.compare_dealer');
	var count = comparedealer.length;
	if (count <=1){
		alert("请至少选择两家经销商进行比较！");
		return false;
	}
	if (count >20){
		alert("至多只能选择20家经销商进行比较！");
		return false;
	}
	var dealer_list = [];
	comparedealer.each(function (n,obj){
		dealer_list.push($(obj).attr('name'));
	});
	dealers = dealer_list.join(',');
	$('#dealer_codes').val(dealers);
	$('#compare').submit();
}

function remove_line()
{
	$('area,a,input[type="button"]').bind('focus',function(){
		if(this.blur){
			this.blur();
			}
	});
}

function download (self)
{
	var dealer_id = $(self).attr('name');
	Boxy.load("/downloadhistoryreports/"+dealer_id+"/",
		{
			"unloadOnHide":true,
			"modal":true,
			"title":"请选择你需要下载的历史报告 Please select the reports which you want download&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
		});
	return false;
}

function isChecked(s) {
	var length = s.length;
	var checked = false;
	for (var i=0;i<length;i++){
		if(s[i].checked==true){
			checked = true;
			break;
		}
	}
	return checked;
}

function downloadfile (self)
{
	var form = $(self).parent('form')[0];
	if (!isChecked(form.report)){
		alert("请至少选择一条记录下载！");
		return false;
	}
	else{
		form.submit();
		Boxy.get(self).hide();
		return false;	
	}

}

//根据期数和品牌搜索经销商和问卷信息
function ajaxFilter(form, divOrHandler) {
    form = form[0];
    if(form.Term.value == ""){
        alert("请选择期数\n\rplease select term");
        return false;
    }
    if(form.Type.value == ""){
        alert("请选择品牌\n\rplease select type");
        return false;
    }
    $.ajax({
       type: form.method,
       url: form.action,
       data: $(form).serialize(),
       success: function(msg){
            if (typeof(divOrHandler) == "undefined") {
                alert(msg);
            }
            else if (typeof(divOrHandler) == "string") {
                $("#"+divOrHandler).html(msg);
            }
            else if (typeof(divOrHandler) == "function") {
                divOrHandler(msg,btn);
            }
       }
    });
    return false;
};

//根据期数和品牌搜索经销商和问卷信息
function ajaxSubmit(form, divOrHandler) {
    form = form[0];
    $.ajax({
       type: form.method,
       url: form.action,
       data: $(form).serialize(),
       success: function(msg){
            if (typeof(divOrHandler) == "undefined") {
                alert(msg);
            }
            else if (typeof(divOrHandler) == "string") {
                $("#"+divOrHandler).html(msg);
            }
            else if (typeof(divOrHandler) == "function") {
                divOrHandler(msg,btn);
            }
       }
    });
    return false;
};