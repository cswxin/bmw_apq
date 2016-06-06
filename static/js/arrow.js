$(document).ready( function () {
	var  clientWidth = document.documentElement.clientWidth || document.body.clientWidth;
	var  bodyWidth = $(".main01").width();
	var  tableWidth = Math.floor(bodyWidth*0.98);
	var  maskWidth = Math.floor((clientWidth-tableWidth)/2);
	var  smallWidth = Math.floor((bodyWidth-tableWidth)/2);
	
	$(".prev").click( function () { 
		     	var adWidthL = $(".forms05").scrollLeft();
				adWidthL = adWidthL-500;
				$(".forms05").scrollLeft(adWidthL);
				var scrollY = -maskWidth-adWidthL-1.5;
				if(adWidthL<1000){scrollY=maskWidth+2;}
				$(".FixedHeader_Header").css("left",scrollY+"px");
				// var example_info = $('#example_info');
				// example_info.css('margin-left', -adWidthL+"px")
				// var example_filter = $('#example_filter');
				// example_filter.css('margin-right', adWidthL+"px")
		 });
		 
	$(".next").click( function () {
 			var adWidthR = $(".forms05").scrollLeft();
 			adWidthR = adWidthR+500;
			$(".forms05").scrollLeft(adWidthR);
			var scrollY = maskWidth-adWidthR+1.5;
	  		if(adWidthR>1500){scrollY=-(fixWidth-tableWidth-maskWidth-1.8);}
			$(".FixedHeader_Header").css("left",scrollY+"px");
			// var example_info = $('#example_info');
			// example_info.css('margin-left', adWidthR+"px")
			// var example_filter = $('#example_filter');
			// example_filter.css('margin-right', -adWidthR+"px")
	});	
	$(".down").click( function () {
            var adHeight = document.body.scrollTop || document.documentElement.scrollTop;
            adHeight = adHeight+500;
            $(window).scrollTop(adHeight);
    });
    $(".up").click( function () {
            var adHeight = document.body.scrollTop || document.documentElement.scrollTop;
            adHeight = adHeight-500;
            if(adHeight<=0){adHeight=0;}
            $(window).scrollTop(adHeight);
    });	
})