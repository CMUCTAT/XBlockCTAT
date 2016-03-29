/**
 * Called by edX to initialize the xblock.
 * @param runtime - provided by EdX
 * @param element - provided by EdX
 */
function Initialize_CTATXBlock(runtime,element) {
    var post = {
	set_variable: function(variable_name,value) {
	    console.log('CTATXBlock.js set_variable');
	    var data = {};
	    data[variable_name] = value;
	    $.post(runtime.handlerUrl(element, 'ctat_set_variable'),
		   JSON.stringify(data)).success(function () {
		       console.log('ctat_set_variable succeeded');
		   });
	},
	report_grade: function(correct_step_count, total_step_count) {
	    console.log('CTATXBlock.js report_grade');
	    $.post(runtime.handlerUrl(element, 'ctat_grade'),
		   JSON.stringify({'value': correct_step_count,
				   'max_value': total_step_count}))
		.success(function () {
		    console.log('ctat_grade succeeded');
		});
	}
    };
    $('.stattutor').load(function() { // this is getting fired after initTutor
	this.contentWindow.CTATTarget = "XBlock"; // needed for ctatloader.js
	var lms = this.contentWindow.CTATLMS;
	lms.identifier = 'XBlock';
	lms.setValue = function(key,value) {
	    CTATConfig[key] = value;
	    post.set_variable(key,value);
	};
	lms.getValue = function(key) { return CTATConfig[key]; };
	lms.saveProblemState = function (state) {
	    post.set_variable('saveandrestore',
			      window.btoa(state.problem_state));
	};
	lms.getProblemState = function (handler) {
	    return handler(window.atob(CTATConfig['saveandrestore']));
	};
	lms.gradeStudent = post.report_grade;
	// CTATConfig is from CTATConfig.js which is a template that is filled
	// out by ctatxblock.py
	this.contentWindow.initTutor(CTATConfig);
    });
};
