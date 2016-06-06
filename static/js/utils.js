function ajaxSubmit(form, divOrHandler) {
    if (form.action == "") {
        form.action = window.location.href;
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
                divOrHandler(msg,form);
            }
       }
    }); 
    return false;
};

function ajaxGet(url, divOrHandler) {
    if (url == "") {
        url = window.location.href;
    }
    $.ajax({
       type: "GET",
       url: url,
       data: "",
       success: function(msg){
            if (typeof(divOrHandler) == "undefined") {
                alert(msg);
            }
            else if (typeof(divOrHandler) == "string") {
                $("#"+divOrHandler).html(msg);
            }
            else if (typeof(divOrHandler) == "function") {
                divOrHandler(msg);
            }                
       }
    });  
    return false;
}

//给定一个dom元素，得到与它最近的指定类型的parent元素(jquery类型)
function get_parent(obj,parent_type) {
    $parent = $(obj).parent();
    while ($parent.length > 0 && $parent[0].nodeName != parent_type.toUpperCase()) {
        $parent = $parent.parent();
    }
    return $parent;
}

//IE中javascript没有indexOf方法
function is_in_list(item, list) {
    for (var i=0;i<list.length;i++) {
        if (list[i] == item) {
            return true;
        }
    }
    return false;
}

function delHtmlTag(str,max_length) 
{ 
    var new_str = str.replace(/<[^>]+>/g,"");//去掉所有的html标记 
    //截断过长在文字
    if (typeof(max_length) == 'undefined' || max_length==0) {
        return new_str;
    }
    else {
        return new_str.substring(0,max_length);
    }
}

function isValidEmail(email) {
    var _reg_email_=/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return _reg_email_.test(email);
}

function set_selected(content){
  $(".nav a:contains('"+content+"')").addClass('selected');
}

function set_submenu(content1,content2,content3){
    $(".question_sidebar a:contains("+content2+"),.question_sidebar a:contains("+content3+")").parent().removeClass("link");
    $(".question_sidebar a:contains("+content1+")").parent().addClass("link");
}

if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, ''); 
  }
}