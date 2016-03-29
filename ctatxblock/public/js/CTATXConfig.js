/*******
 * This is to be loaded after ctat.min.js but before calling initTutor in
 * the XBlock environment.
 *
 * window.parent.CTATConfig is defined in static/html/ctatxblock.html which
 * is a template expanded and added by ctatxblock.py
 *
 * window.parent.CTATXBlock is defined in static/js/CTATXBlock.js which is
 * added and executed by ctatxblock.py
 */

/** set the environment */
var CTATXConfig = window.parent.CTATConfig; // grab from encompasing environment

/*CTATLMS.identifier = 'XBlock';
CTATLMS.setValue = function(key,value) {
    // update "local" copy as well because xblock does not update the
    // templated values durring runtime.
    CTATXConfig[key] = value;
    return window.parent.CTATXBlock.post.set_variable(key,value);
};
CTATLMS.getValue = function(key) { return CTATXConfig[key]; };
CTATLMS.saveProblemState = function (state) {
    CTATLMS.setValue('saveandrestore',window.btoa(state));
};
CTATLMS.getProblemState = function (handler) {
    return handler(window.atob(CTATLMS.getValue('saveandrestore')));
};
CTATLMS.gradeStudent = window.parent.CTATXBlock.post.report_grade;*/
