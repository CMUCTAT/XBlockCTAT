
var xblockRuntime=null;
var xblockElement=null;
var xblockpointer=null;

/**
 *
 */
function setVariable (aVariable,aContent)
{
	console.log ("setVariable ("+aVariable+")");

	var encoded=window.btoa (aContent);

	//console.log ("Encoded: " + encoded);

	console.log ("Constructed xblock handler url: " + xblockRuntime.handlerUrl(xblockElement,
			"ctat_set_variable"), JSON.stringify({aVariable:encoded}));

	$.ajax({
		type: "POST",
		url: xblockRuntime.handlerUrl(xblockElement, "ctat_set_variable"),
		data: JSON.stringify({aVariable:encoded}), //"{\""+ aVariable + "\": \"" + encoded + "\"}",
		success: function(result)
		{
			console.log ("success");
			//introspect ("xblockresult",result," ",2);
		},
		error: function (obj,textStatus,errorThrown)
		{
			console.log ("Error calling XBlock handler: " + errorThrown);
		}
	});
}

/**
 *
 */
function CTATXBlock(runtime, element)
{
	console.log("CTATXBlock ("+runtime+","+element+") (STUDIO)");

	xblockRuntime=runtime;
	xblockElement=element;
	xblockpointer=this;

	var pointer=this;
	
	$('#brd').on('input', function() 
	{
		console.log ("Setting brd to: " + $('#brd').text ());
		
		setVariable ("href",$('#brd').text ()));
	});
	
	$('#module').on('input', function() 
	{
		console.log ("Setting module to: " + $('#module').text ());
		
		setVariable ("module",$('#module').text ()));
	});	
}
