
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
function CTATXBlockStudio(runtime, element)
{
	console.log("CTATXBlockStudio ("+runtime+","+element+") (STUDIO)");

	xblockRuntime=runtime;
	xblockElement=element;
	xblockpointer=this;

	var pointer=this;
	
	applyValues ();
	
	$("#diskdir").prop( "disabled", true);
	$("#port").prop( "disabled", true);
	$("#remoteurl").prop( "disabled", true);

	$("#drop").change(function () 
	{
        var logsetting = $('#drop option:selected').val();
		
		console.log ("Log setting chosen: " + logsetting);        
		
		if (logsetting=="javascript")
		{
			$("#diskdir").prop( "disabled", true);
			$("#port").prop( "disabled", true);
			$("#remoteurl").prop( "disabled",true);
		}
		else		
		{
			$("#diskdir").prop( "disabled", false);
			$("#port").prop( "disabled", false);
			$("#remoteurl").prop( "disabled", false);
		}
    });	
	
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
