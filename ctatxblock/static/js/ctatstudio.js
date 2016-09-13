/**
 *
 */
function CTATXBlockStudio(runtime, element)
{
    $(element).find('.save-button').bind('click', function() {
	var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
	var data = {
	    src: $(element).find('input#interface').val(),
	    brd: $(element).find('input#brd').val(),
	    width: $(element).find('input#maxwidth').val(),
	    height: $(element).find('input#maxheight').val(),
	    logging: $(element).find('input#logging').is(':checked'),
	    logserver: $(element).find('input#log_url').val(),
	    dataset: $(element).find('input#log_dataset').val(),
	    problemname: $(element).find('input#log_name').val(),
	    custom: $(element).find('textarea#extra').val()
	};
	if (data.src.trim().length <= 0) {
	    alert('Interface file needs to be not empty.');
	    return;
	}
	if (data.brd.trim().length <=0) {
	    alert('BRD file needs to be not empty.');
	    return;
	}
	var w = Number(data.width);
	if (isNaN(w) || w<100) {
	    alert('Width should be at least 100.');
	    return;
	}
	var h = Number(data.height);
	if (isNaN(h) || h<100) {
	    alert('Height should be at least 100.');
	    return;
	}
	if (data.logging) {
	    if (data.logserver.trim().length <= 0) {
		alert('When logging is enabled, a log service needs to be specified.');
		return;
	    }
	    if (data.dataset.trim().length <= 0) {
		alert('When logging is enabled, a dataset name needs to be specified.');
		return;
	    }
	    if (data.problemname.trim().length <= 0) {
		alert('When logging is enabled, a problem name needs to be specified.');
		return;
	    }
	}
	if (data.custom) {
	    try {
		JSON.parse(data.custom);
	    } catch(err) {
		alert('Invalid JSON in Extra Parameters: ' + err);
		return;
	    }
	}
	console.log(runtime);
	if (runtime.notify)
	    runtime.notify('save', {state: 'start'});
	$.post(handlerUrl, JSON.stringify(data)).done(function(response) {
	    if (response['result'] != 'success') {
		console.log(response);
		if (response['error']) {
		    alert(response['error']);
		} else {
		    alert('Save failed!');
		}
	    }
	}).fail(function() {
	    alert("Error in posting configuration parameters!");
	}).always(function() {
	    if (runtime.notify)
		runtime.notify('save', {state: 'end'});
	});
    });

    $(element).find('.cancel-button').bind('click', function() {
	runtime.notify('cancel', {});
    });
}
