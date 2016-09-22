/**
 * Called by edX to initialize the xblock.
 * @param runtime - provided by EdX
 * @param element - provided by EdX
 */
function Initialize_CTATXBlock(runtime, element) {
    var post = {
	save_problem_state: function(state) {
	    //console.log('save_problem_state',state);
	    $.ajax({type: "POST",
		    url: runtime.handlerUrl(element, 'ctat_save_problem_state'),
		    data: JSON.stringify({state:state}),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json"});
	},
	report_grade: function(correct_step_count, total_step_count) {
	    //console.log('grade',correct_step_count,total_step_count);
	    $.ajax({type: "POST",
		    url: runtime.handlerUrl(element, 'ctat_grade'),
		    data: JSON.stringify({'value': correct_step_count,
					  'max_value': total_step_count}),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json"});
	},
	log_event: function(aMessage) {
	    $.ajax({type: "POST",
		    url: runtime.handlerUrl(element, 'ctat_log'),
		    data: JSON.stringify({
			'event_type': 'ctat_log',
			'action': 'logevent',
			'message': aMessage}),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json"})
		.done(function(data) {
		    console.log('success on ctat_log: '+data.result);
		})
		.fail(function() {
		    console.log('fail on ctat_log');
		});
	},
	report_skills: function(skills) {
	    $.ajax({type: "POST",
		    url: runtime.handlerUrl(element, 'ctat_save_skills'),
		    data: JSON.stringify({'skills': skills}),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json"});
	}
    };
    $('.ctatxblock').on("load", function() {
	var ctattutor = new URL(this.src);
	// put problem state in config
	this.contentWindow.postMessage(CTATConfig, ctattutor.origin);

	window.addEventListener("message", function(event) {
	    if (event.origin !== ctattutor.origin) {
		console.log("Message not from valid source:", event.origin,
			    "Expected:", ctatttuor.origin);
		return;
	    }
	    switch (event.data.action) {
	    case "save_problem_state":
		post.save_problem_state(event.data.input);
		break;
	    case "grade":
		post.report_grade(event.data.input.value, event.data.input.max);
		break;
	    case "log":
		post.log_event(event.data.input);
		break;
	    case "skills":
		post.report_skills(event.data.input);
		break;
	    default:
		console.log("unrecognized action:", event.data.action);
		break;
	    }
	}, false);
    });
}
