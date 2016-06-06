function realLength(strVal) {
    var tempStr ;
    tempStr = strVal.replace(/(^\s*)|(\s*$)/g, '');
    return tempStr.replace(/[^\x00-\xff]/g,"**").length;
}

String.prototype.trim = function () {
    return this.replace(/^\s*/, "").replace(/\s*$/, "");
}

//---------------------------------------------------字符是否在S中
function isCharsInBag (s, bag) { 
    var i;

    for (i = 0; i < s.length; i++){ 
    // Check that current character isn't whitespace.
        var c = s.charAt(i);
        if (bag.indexOf(c) == -1) return false;
    }
    return true;
}

function isEmpty(s) {
    return ((s == null)||(s.length == 0)||realLength(s)==0); 
}

//----------------------------------------------------闰年判断
function isleapyear(thisyear)
{
return(((thisyear%4==0) && (thisyear%100!=0)) || (thisyear%400==0))

}

//--------------------------------------------------数字判断
function isNum(s,length) {
    if (isEmpty(s)){ 
        return false;
    }
    if(!isCharsInBag (s, "0123456789")){
        return false;
    }
    if (typeof(length) == 'undefined') {
        return true;
    }
    if (s.length != length) {
        return false;
    }
    return true;
}

function isRadioSelected(radio_input) {
    for (i=0;i<radio_input.length;i++) {
        if (radio_input[i].checked) {
            return true;
        }
    }
    return false;
}

function CheckInput(thefield)
{
	 var flag;
	 var i;
	 flag="true";
	 var Fvalue=thefield.value;
	 if(isNaN(Fvalue.replace(".","")))
	 {
		flag="false";
	 }
	 else
	 {
		if(Fvalue.indexOf(".")==-1)
		{
			//未找到小数点
			flag="false";	
		}
		else
		{
			if( (Fvalue.length-Fvalue.indexOf(".")-1)!=2)
			{
				//小数位不是2
				flag="false";	
			}
		}
	 }
	 return flag;
}

function set_radio(radio,value){
	for (var i=0;i<radio.length;i++){
		if (radio[i].value == value){
			radio[i].checked = true;
		}
	}
}

function check_radio(form_obj,question,show){
    if (!isRadioSelected(form_obj[question])) {
        alert("请选择"+show+"！");
        form_obj[question][0].focus();
        return false;
    }
    
    if (form_obj[question][1].checked || (typeof(form_obj[question][2]) != "undefined" && form_obj[question][2].checked)) {
        if (typeof(form_obj[question+"__open"]) != "undefined" && isEmpty(form_obj[question+"__open"].value)) {
            alert("请输入"+show+"选择'否/不适用'的原因！");
            if (form_obj["input_"+question] != null){
                form_obj["input_"+question].focus();
            }else{
                form_obj[question+"__open"].focus();
            }
            return false;
        }
    }
	return true;
}

function re_no_answer(form_obj,no_list){
    for (var i=0; i < no_list.length; i++) {
        text = form_obj[no_list[i]+"__open"].value;
        text = text.split("^-^");
        text = text[text.length-1];
        form_obj[no_list[i]+"__open"].value = text;
    }
}

function set_no_answer(form_obj,qid){
    var _value = '';
    for (var i = 0;i<form_obj["ck_"+qid].length;i++){
        if (form_obj["ck_"+qid][i].checked){
            _value += (form_obj["ck_"+qid][i].value+'^-^');
        }
    }
    text = form_obj["input_"+qid].value;
    _value += text;
    if (!form_obj[qid][0].checked&&_value!=''){
        form_obj[qid+"__open"].value = _value;
    }
}

function off_check(qid){
    form_obj = $("#paper_form input[name='ck_"+qid+"']");
    text_obj = $("#paper_form input[name='input_"+qid+"']");
    for (var i=0; i < form_obj.length; i++) {
        form_obj[i].checked = false;
        form_obj[i].disabled = true;
    };
    text_obj[0].value = '';
}

function on_check(qid){
    form_obj = $("#paper_form input[name='ck_"+qid+"']");
    for (var i=0; i < form_obj.length; i++) {
        form_obj[i].disabled = false;
    };
}
