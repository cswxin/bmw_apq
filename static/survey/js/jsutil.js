var org_cd;  //Big type
var mid_cd;  //Middle type
var CompanyItem;//责任部门分类，数组

function W_Close()
{
	this.close();
	return false;
}

function AcceptPrint() {
	factory.printing.header = "";
	factory.printing.footer = "";
	factory.printing.portrait = false;
	factory.printing.leftMargin = 15;
	factory.printing.topMargin = 10  ;
	factory.printing.rightMargin = 15 ; 
	factory.printing.bottomMargin = 10 ;
	factory.printing.Print(false, window);
}
				
function js_ClientWinOpen(sUrl, sName, sOpt)
{
	window.open (sUrl, sName, sOpt);
	return true;
}

function OpenInputWindow(url)
{
	window.open(url,"","Height=650,Width = 698,scrollbars=yes,left=150,top=60");
	void(0);
}

function OpenSTSHistoryWindow(url)
{	
	window.open(url,"","Height=410,Width =700,scrollbars=yes,left=150,top=0");
	void(0);
}

function OpenAPWindow(url)
{
	window.open(url,"","Height=680,Width =700,scrollbars=yes,left=150,top=0");
	void(0);
}

function OpenReportWindow(url)
{
	//var url = "/front/web/Report/report06_01.aspx?VOC_ORG=Root.服务AAAAA&STARTDATE=2005-07-13&ENDDATE=2005-07-19"
    var urlLen = url.length;
	var index_1 = url.indexOf("="); //获得第一个=号所在的位置
	var index_2 = url.indexOf("&");//获得第一个&号所在的位置
	
	var str1 = url.substring(index_1+1,index_2); //Root.服务AAAAA
	var str2 = encodeURI(str1);
	var str3 = url.substring(index_2,urlLen); //第一个&在的地到串尾 --&STARTDATE=2005-07-13&ENDDATE=2005-07-19
	var str4 = url.substring(0,index_1+1);
	
	var strUrl = str4 + str2 + str3;
	
	//alert(strUrl);
	
	window.open(strUrl,"","Height=650,Width = 850,scrollbars=yes,left=150,top=0");
	void(0);
}

function OpenReportWindow_LIST(url)
{
	window.open(url,"","Height=650,Width = 900,scrollbars=yes,left=100,top=0");
	void(0);
}

function OpenHistoryWindow(url)
			{
				//var vid = document.Form1.txtinnerVocid.value;
				//var url = "inner_voc_his_list.aspx?InnerVocid=" + vid;
				window.open(url,"","Height=700,Width = 700,scrollbars=yes,left=150,top=0");	
				
				void(0);
			}
			
function OpenReport03(url)
{
	//var bb = encodeURI(url)
	//alert(bb);
	var bb = url;
	window.open(bb,"","Height=650,Width =880,scrollbars=yes,left=150,top=0");	
	void(0);
}

function OpenReport04(url,id)
{
	var bb = encodeURI(url)
	//alert(bb);
	bb = bb + "%3fhidden%3dtrue%26id%3d" + id
	//alert(bb);
	window.open(bb,"","Height=650,Width =880,scrollbars=yes,left=150,top=0");	
	void(0);
}

function valid_email(email)
{
	if(trim(email) == "")
		return false;
		
	if(email.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+([\.][a-z0-9]+)+$") == null)
		return false;

	return true;
}

function valid_numeric(number)
{
	if (number.match(/\D/) != null)
		return false;
	else
		return true;
}

// trim

function trim(strIn)
{
	var strOut = "";

	if (strIn)
		strOut = strIn.replace(/^\s*/,'').replace(/\s*$/, ''); 
	
	return strOut;
}

function DoChkAll(sIDPreFix)
{
	var chkIdIs = "";
	
	for (i=0; i < document.forms[0].length; i++)
	{
		var objCtrl = document.forms[0][i];
		
		if (objCtrl.type == "checkbox" && objCtrl.name.indexOf(sIDPreFix) > -1)
		{
			if (objCtrl.checked)
				objCtrl.checked = false;				
			else
				objCtrl.checked = true;			
		}
	}
}

function ClipBoardCopy(sTarId)
{
	var srcItem = document.getElementById(sTarId);
	ClipBoardCopyAtObj (srcItem);
}
function ErrInputProc(objCont)
{
	objCont.focus();
	return false;	
}

function GetControlByOtherForm(objDoc, sTarId)
{
	
	for (i=0; i < objDoc.forms[0].length; i++)
	{
		if (objDoc.forms[0][i] && objDoc.forms[0][i].name.indexOf(sTarId) > -1)
		{
			return objDoc.forms[0][i];
		}
	}
	
	return null;
}
function go_url(url) {
		show_progressbar();
		location.href = url;
		
}

function floatRound(myFloat,mfNumber) 
{ 
	if ( mfNumber == 0 ) 
		return Math.round(myFloat); 
	else { 
		var cutNumber = Math.pow(10,mfNumber); 
		return Math.round(myFloat * cutNumber)/cutNumber; 
		} 
}	

function js_convertDate(strDate)
{
	if(strDate.length==1)
		return  "0" + strDate ;
	else
		return strDate;	

}

function GetDaysOfMonth(year,month)
{
	var iYear = parseInt(year,10);
	//是否是闰年
	var bRN = false;
	if ((iYear%4==0 && iYear%100!=0) || iYear%400==0)
	{
		bRN = true;
	}

	var iMonth = parseInt(month,10);
	switch(iMonth)
	{
		case 1:
		case 3:
		case 5:
		case 7:
		case 8:
		case 10:
		case 12:
				return 31;
		case 2:
				if (bRN)
					return 29;
				else
					return 28;
		default:
				return 30;
	}	
}

function lrtrim(src)
{
    var search = 0

    while ( src.charAt(search) == " ")
    {
        search = search + 1
    }

    src = src.substring(search, (src.length))

    search = src.length - 1

    while (src.charAt(search) ==" ")
    {
        search = search - 1
    }

    return src.substring(0, search + 1)
}



function calPopForCMon(name, target)
{
	dateName = target;
	var strDate = lrtrim(name.value);
	var DateYear = "";
	var DateMonth = "";
	var DateDay = "";
	if(strDate == "")
	{
		callCalPop(name, target);
	}
	else
	{
		var ArrDate = strDate.split("-");

		DateYear  = ArrDate[0];
		DateMonth = ArrDate[1];
		DateDay   = ArrDate[2];
		
		if(!isNumber(DateMonth)){
			DateMonth = 1;
		}
		
		if(!isNumber(DateDay)){
			DateDay = 1;
		}
		
		if(!isNumber(DateYear)){
			DateYear = 2005;
		}
		
		
		if(DateMonth > 12){
			DateMonth = 1;	
		}
		
		if(DateDay > 31){
			DateDay = 1;	
		}
		
		try
		{
			DateMonth = DateMonth / 1;
		}
		catch(e)
		{
			DateMonth = 1;
		}
		
		if(DateMonth < 9 ){
			DateMonth = "0" + DateMonth;
		}

		callCalPopForCMon(name, target, DateYear, DateMonth, DateDay);
	}
}


function isNumber(pObj){
	var obj = pObj;
	strRef = "1234567890";
	for (i=0;i<obj.length;i++) {
		tempChar= obj.substring(i,i+1);
		if (strRef.indexOf(tempChar,0)==-1) {
			return false; 
			}
	}
	return true;
}

function setCalDate(targetName, returnStr)
{
	eval(targetName).value = returnStr;

	try
	{
		if(dateName == "setStartDate")
		{
			frmSchedule.endDate1.value = frmSchedule.startDate1.value;
		}
	}
	catch(e)
	{
	}
	finally
	{
	//	if(cTab == "1")
	//	{
	//		resetBlankTime(returnStr);
	//	}
	//	dateName = "";
	}
}

/*
function ShowLDAPPage() {
	var drmOptionObject = new Object();
	var MDUrl = "/ldap/ldap.asp";
	var sFeatures = "dialogWidth:688px;dialogHeight:650px;scroll:on;status:off;resizable:yes;";
	window.showModalDialog(MDUrl, drmOptionObject, sFeatures);
}*/


function ShowLDAPPage() {
	var drmOptionObject = new Object();
	var MDUrl = "/Comm/LDAP/ldap.asp";
	var newWin = window.open(MDUrl,"voc_ldap","width=696,height=610,top=150,left=0,toolbar=no, menubar=no, scrollbars=yes,resizable=no,location=no, status=no","yea");
	var windowX = Math.ceil( (window.screen.width - 696) / 2 );
	var windowY = Math.ceil( (window.screen.height - 640) / 2 );
	newWin.moveTo(windowX,windowY);
	try
	{
		newWin.focus();
	}catch(e)
	{
	}
}

function ShowAPPage() {
	var drmOptionObject = new Object();
	var MDUrl = "/Comm/AP/LDap.asp";
	var newWin = window.open(MDUrl,"voc_ap","width=696,height=610,top=100,left=60,toolbar=no, menubar=no, scrollbars=yes,resizable=no,location=no, status=no","yea");
	var windowX = Math.ceil( (window.screen.width - 696) / 2 );
	var windowY = Math.ceil( (window.screen.height - 640) / 2 );
	newWin.moveTo(windowX,windowY);
	try
	{
		newWin.focus();
	}catch(e)
	{
	}
}

function ShowAPListPage(strValue) {
		var drmOptionObject = new Object();
		var MDUrl = "/Comm/AP/ldap_list.aspx?slt_field1=cn&txt_value1=" + encodeURI(strValue + "AAAAA");
		//alert(MDUrl);
		var newWin = window.open(MDUrl,"voc_ap_list","width=696,height=610,top=100,left=60,toolbar=no, menubar=no, scrollbars=yes,resizable=no,location=no, status=no","yea");
		var windowX = Math.ceil( (window.screen.width - 696) / 2 );
		var windowY = Math.ceil( (window.screen.height - 640) / 2 );
		newWin.moveTo(windowX,windowY);
		try
		{
			newWin.focus();
		}catch(e)
		{
		}
}

//==========================================================================//
//code by cwy(for open "SelectDialog.aspx")
function ShowSelectPage(){
	var MDUrl = "/front/web/Search/SearchGetList.aspx";
	var newWin = window.open(MDUrl,"voc_select","width=696,height=610,top=100,left=60,toolbar=no, menubar=no, scrollbars=yes,resizable=no,location=no, status=no","yea");
	var windowX = Math.ceil( (window.screen.width - 696) / 2 );
	var windowY = Math.ceil( (window.screen.height - 640) / 2 );
	newWin.moveTo(windowX,windowY);
	try
	{
		newWin.focus();
	}catch(e)
	{
	}
}
//==========================================================================//


function mOvr(src,clrOver,clrOver1) {
	if (!src.contains(event.fromElement)) 
	{
	src.style.cursor = 'hand'; src.bgColor = clrOver;
	src.style.color = clrOver1;
	}
}
function mOut(src,clrIn,clrIn1) {
	if (!src.contains(event.toElement))
	{
	src.style.cursor = 'default'; src.bgColor = clrIn; 
	src.style.color = clrIn1;
	}
}
function mClk(src) {
	if(event.srcElement.tagName=='TD')
	{
	src.children.tags('A')[0].click();
	}
}

/*this javascript for ldap page */
function DeleOption(objSelectOption){
	var objLenght = 0;
	var Flag = 0;
	var objDescSelect = document.all[objSelectOption];

	for(i=0; i<objDescSelect.options.length; i++){
		if(objDescSelect.options[i].selected){
			objDescSelect.remove(i);
		}
	}
	for(i=0; i<objDescSelect.options.length; i++){
		if(objDescSelect.options[i].selected){
			objDescSelect.remove(i);
		}
	}
	for(i=0; i<objDescSelect.options.length; i++){
		if(objDescSelect.options[i].selected){
			objDescSelect.remove(i);
		}
	}
	for(i=0; i<objDescSelect.options.length; i++){
		if(objDescSelect.options[i].selected){
			objDescSelect.remove(i);
		}
	}
}

/*this javascript for ldap page */
function DeleParentOption(objSelectOption){
	var objLenght = 0;
	var Flag = 0;
	var objDescSelect = window.opener.document.all[objSelectOption];
	
	for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
	for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
}

function DeleParentOption1(objSelectOption){
	var objLenght = 0;
	var Flag = 0;
	var objDescSelect = window.parent.window.document.all[objSelectOption];
	
	for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
	for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
		for(i=0; i<objDescSelect.options.length; i++){
			objDescSelect.remove(i);
	}
}

function AutoDeleValueIsNullOption(objSelectOption){
	var objLenght = 0;
	var Flag = 0;
	var objDescSelect = document.all[objSelectOption];
    
    var strValue = "";
	for(i=0; i<objDescSelect.options.length; i++){
		if(objDescSelect.options[i].value == ""){
			objDescSelect.remove(i);
		}
	}
}

//if double click select,open url
function DBClickOpenURL(objSelectOption)
{	
	var objDescSelect = document.all[objSelectOption];
	var url = "";
	var name = "";
	for(i=0; i<objDescSelect.options.length; i++){
		if(objDescSelect.options[i].selected)
		{
			url  = encodeURI(objDescSelect.options[i].value);			
			name = encodeURI(objDescSelect.options[i].text);
			var k = name.lastIndexOf('.');
			var subName = name.substring(k-14,k);
			name=name.replace(subName,"");
		}
	}
	
	if(url!="")
	{
		window.open("/Comm/DownLoadAttach.aspx?FilePath="+url+"&FileName="+name);
	}	
}

//===================================================================================================
//==CREATED By ChenZhiChao
//==CEEATED Date 2005-07-11
//==Description:验证日期的有效性，可验证润年
//===================================================================================================

function isdate(strDate)
{
	var m;
	var op = strDate;
	var yearFirstExp = new RegExp("^\\s*((\\d{4})|(\\d{2}))([-/]|\\. ?)(\\d{1,2})\\4(\\d{1,2})\\s*$");
    m = op.match(yearFirstExp);
    var day, month, year;
        
        if(m == null)
        {
			return null;
        }
		if (m != null && (m[2].length == 4 || val.dateorder == "ymd")) {
            day = m[6];
            month = m[5];
            year = (m[2].length == 4) ? m[2] : GetFullYear(parseInt(m[3], 10))
        }
        else {
            if (val.dateorder == "ymd"){
                return null;		
            }						
            var yearLastExp = new RegExp("^\\s*(\\d{1,2})([-/]|\\. ?)(\\d{1,2})\\2((\\d{4})|(\\d{2}))\\s*$");
            m = op.match(yearLastExp);
            if (m == null) {
                return null;
            }
            if (val.dateorder == "mdy") {
                day = m[3];
                month = m[1];
            }
            else {
                day = m[1];
                month = m[3];
            }
 
            year = (m[5].length == 4) ? m[5] : GetFullYear(parseInt(m[6], 10))
        }
        month -= 1;
        if(year < 1900)
        {
			return null;
        }
        var date = new Date(year, month, day);
        return (typeof(date) == "object" && year == date.getFullYear() && month == date.getMonth() && day == date.getDate()) ? date.valueOf() : null;

}
function GetFullYear(year) 
{
	return (year + parseInt(val.century)) - ((year < val.cutoffyear) ? 0 : 100);
}


////////////////////////////分态分类组件/////////////////////////////////

function loadXML(vocType)
{
	var xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
	xmlDoc.async="false";
	//alert("/front/web/emergencyvoc/sort_XML.aspx?VOCTYPE=" + vocType);
	xmlDoc.load("/front/web/emergencyvoc/sort_XML.aspx?VOCTYPE=" + vocType);
	//xmlDoc.load("class.xml");
	xmlObj=xmlDoc.documentElement; 
	nodes = xmlDoc.documentElement.childNodes;
	document.all["org"].options.length = 0; 
	document.all["mid"].options.length = 0;

	for (i=0;i<xmlObj.childNodes.length;i++)
	{
		labels=xmlObj.childNodes(i).getAttribute("name");
		values=xmlObj.childNodes(i).getAttribute("value");
		document.all["org"].add(document.createElement("OPTION"));
		if(i==0)
		{
			document.all["org"].add(document.createElement("OPTION"));
			document.all["org"].options[0].text="璇烽�夋嫨"; 
			document.all["org"].options[0].value=""; 
			
			document.all["org"].options[i+1].text=labels; 
			document.all["org"].options[i+1].value=values; 
		}
		else
		{
			document.all["org"].options[i+1].text=labels; 
			document.all["org"].options[i+1].value=values; 
		}
	}
	
}


function setmin(main)
		{
			var is_selected="N";
			document.all["mid"].length=0;
			document.all["sml"].length=0;

			for (i=0;i<xmlObj.childNodes.length;i++)
			{

				var values="";
				var lables="";

				//if (is_selected=="Y") return;
				labels=xmlObj.childNodes(i).getAttribute("name");
				values=xmlObj.childNodes(i).getAttribute("value");
				if (labels==main)
				{

					is_selected="Y";

					for (j=0;j<xmlObj.childNodes(i).childNodes.length;j++)
					{
						labels=xmlObj.childNodes(i).childNodes(j).getAttribute("name");
						values=xmlObj.childNodes(i).childNodes(j).getAttribute("value");
						
						if (labels != "")
						{
							if(j==0)
							{
								document.all["mid"].add(document.createElement("OPTION"));
								document.all["mid"].options[0].text="璇烽�夋嫨"; 
								document.all["mid"].options[0].value=""; 
								
								document.all["mid"].add(document.createElement("OPTION"));
								document.all["mid"].options[j+1].text=labels; 
								document.all["mid"].options[j+1].value=values; 
							}
							else
							{
								document.all["mid"].add(document.createElement("OPTION"));
								document.all["mid"].options[j+1].text=labels; 
								document.all["mid"].options[j+1].value=values; 
							}
						}
					}
				}
			  }
				
			}
			
			function setsml(main,voc_type,product_cd)
			{
				//alert("a");
				//var is_selected="N";
				document.all["sml"].length=0;

				for (i=0;i<xmlObj.childNodes.length;i++)
				{

					var values="";
					var lables="";

					//if (is_selected=="Y") return;

					//alert(labels+ " | "+main);
					for (j=0;j<xmlObj.childNodes(i).childNodes.length;j++)
					{
						labels=xmlObj.childNodes(i).childNodes(j).getAttribute("name");
						values=xmlObj.childNodes(i).childNodes(j).getAttribute("value");
						if (labels==main)
						{

							is_selected="Y";

							for (k=0;k<xmlObj.childNodes(i).childNodes(j).childNodes.length;k++)
							{
								//subclass_name="document.frm.subclass";
								labels=xmlObj.childNodes(i).childNodes(j).childNodes(k).getAttribute("name");
								values=xmlObj.childNodes(i).childNodes(j).childNodes(k).getAttribute("value");
								
								if(labels != "")
								{
									if(k==0)
									{
										document.all["sml"].add(document.createElement("OPTION"));
										document.all["sml"].options[0].text="璇烽�夋嫨"; 
										document.all["sml"].options[0].value=""; 
										
										document.all["sml"].add(document.createElement("OPTION"));
										document.all["sml"].options[k+1].text=labels; 
										document.all["sml"].options[k+1].value=values; 
									}
									else
									{
										document.all["sml"].add(document.createElement("OPTION"));
										document.all["sml"].options[k+1].text=labels; 
										document.all["sml"].options[k+1].value=values; 
									}
								}

							}

						}
					}
					
				}
				
				var oSel_ORG=document.all("org");
				var oSel_MID=document.all("mid");
				
				
				with (oSel_ORG)
				{
					org_cd = encodeURI(options[selectedIndex].value);
				}
				with (oSel_MID)
				{
					mid_cd = encodeURI(options[selectedIndex].value);
				}
				try
				{
					
					var odlProd = document.all("dlProd");
					
					if(product_cd == "" || product_cd == null){
						if(odlProd.options.selectedIndex == 0)
						{
							alert("pls choose product list!");
							var oSel_MID=document.all("mid");
				
							with (oSel_MID)
							{
								options.selectedIndex=0;
							}
							return false;
						}
						with (odlProd)
						{
							product_cd = encodeURI(options[selectedIndex].value);
						}
					}
					
				}
				catch(e)
				{
					
				}
				//var url="/comm/ldap/ldap_iframe.aspx?a=a&LARGE_CD=" + org_cd + "&MID_CD=" + mid_cd +"&PROD_CD=" + product_cd + "&VOC_TYPE=" + voc_type;
				//alert(url);
				//frame1.location.replace(url);
			}
			
			
			function showval()
			{
				var oSel_ORG=document.all("org");
				var oSel_MID=document.all("mid");
				var oSel_SML=document.all("sml");
				try
				{
					if(oSel_ORG != null)
					{
						with (oSel_ORG)
						{
						document.all("hidORG").value=options[selectedIndex].value;
						}
					}
					if(oSel_MID != null)
					{
						with (oSel_MID)
						{
						document.all("hidMID").value=options[selectedIndex].value;
						}
					}
					if(oSel_SML != null)
					{
						with (oSel_SML)
						{
						document.all("hidSML").value=options[selectedIndex].value;
						}
					}
				}
				catch(e)
				{
				}
			}
			
			function setdefaultVal(defaultVal)
			{
					var pin=0;
					for(count=0;count<document.all("org").options.length ; count++)
					{
						if(document.all("org").options[count].text ==defaultVal)
						{
							pin=count;
						}
					}
					document.all("org").options.selectedIndex=pin;
					setmin(defaultVal);
			}
			
			function setSelect(val,id)
			{
					var pin=0;
					for(count=0;count<id.options.length ; count++)
					{
						if(id.options[count].value ==val)
						{
							pin=count;
						}
					}
					
					id.options.selectedIndex=pin;
			}

///////////////////////////////责任部门分类//////////////////////////////////////
//选择公司后，更新部门列表

			function setcom(parent,item)
			{
				var num_1=1;
				var otherTxt;
				var otherVal;
				var num=0;
				
				CompanyItem=item;
				parent.length=0;
				parent.add(document.createElement("OPTION"));
				parent.options[0].text="璇烽�夋嫨"; 
				parent.options[0].value=""; 
				//alert("鍏跺畠");
				/*
				for(i=0; i < item.length ; i++)
				{
					if(item[i][0]=="0")
					{
						if(item[i][2] != "鍏跺畠")
						{
							parent.add(document.createElement("OPTION"));
							parent.options[num].text=item[i][2]; 
							parent.options[num].value=item[i][1]; 
							num=num+1;
						}
						else
						{
							otherTxt=item[i][2]; 
							otherVal=item[i][1]; 
							//alert(item[i][2]);
						}
					}
				}
				parent.add(document.createElement("OPTION"));
				parent.options[num].text=otherTxt; 
				parent.options[num].value=otherVal; 
				*/
				
				for(i=0; i < item.length ; i++)
				{
					if(item[i][0]=="0")
					{
						
						parent.add(document.createElement("OPTION"));
						parent.options[num_1].text=item[i][2]; 
						parent.options[num_1].value=item[i][1]; 
						num_1=num_1+1;
					}
				}
			}
			function setdept()
			{
				var num=1;
				var parent=document.all["selCompany"];
				var child=document.all["selDept"];
				child.length=0;
				child.add(document.createElement("OPTION"));
				child.options[0].text="璇烽�夋嫨"; 
				child.options[0].value=""; 

				for(i=0; i < CompanyItem.length ; i++)
				{
					if(CompanyItem[i][0]==parent.options[parent.selectedIndex].value)
					{
						child.add(document.createElement("OPTION"));
						child.options[num].text=CompanyItem[i][2]; 
						child.options[num].value=CompanyItem[i][1]; 
						num=num+1;
					}
				}
			}
			
			function setval()
			{
				var parent=document.all["selCompany"];
				var child=document.all["selDept"];
				document.all("hidCom").value=parent.options[parent.selectedIndex].value;
				document.all("hidDept").value=child.options[child.selectedIndex].value;
			}
			function DBClickOpenVOC(objSelectOption)
			{   
				var objDescSelect = document.all[objSelectOption];
				var voc = "";
				var vocid = "";
				var MDUrl = "";
				var objArray;
				for(i=0; i<objDescSelect.options.length; i++)
				{
					if(objDescSelect.options[i].selected)
					{
						voc  = document.all.lstXgVoc.options[i].value;						
					}
				}
				if(voc!="")
				{
					objArray = voc.split("|");
					vocid = objArray[0];
					if(objArray[1] == "STS")
					{
						MDUrl = "/front/web/EmergencyVoc/sts_voc_department.aspx?hidden=true&id="+vocid;
					}
					if(objArray[1] == "DIRECT")
					{
						MDUrl = "/front/web/EmergencyVoc/direct_voc_department.aspx?hidden=true&id="+vocid;
					}
					if(objArray[1] == "INTERNET")
					{
						MDUrl = "/front/web/EmergencyVoc/int_voc_department.aspx?hidden=true&id="+vocid;
					}
					if(objArray[1] == "INNER")
					{
						MDUrl = "/front/web/EmergencyVoc/Inner_voc_department.aspx?hidden=true&id="+vocid;
					}
					var varWidth=696;
					var varHeight=713;
					var varLeft=Math.ceil( (window.screen.width -696) / 2 );
					var varTop=0;

					var newWin = window.open(MDUrl,"","width="+ varWidth 
								+",height="+ varHeight +",top="+ varTop +",left="+ varLeft 
								+",toolbar=no, menubar=no, scrollbars=yes,resizable=no,location=no, status=no","yea");
					try
					{
						newWin.focus();
					}
					catch(e)
					{
					}
				}
			}
			
////////////////////////////////////////////////////////////////////////////////////////////////////////


//======================================================================================================================================