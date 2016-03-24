/*******
 * This is to be loaded after ctat.min.js but before calling initTutor in
 * the XBlock environment.
 */

/** set the environment */
var CTATTarget="XBlock"; // this should eventually be removed
var CTATXConfig = window.parent.CTATConfig; // grab from encompasing environment
//setVariable = window.parent.CTATXBlock.post.set_variable;
//getVariable = function(key) { return window.atob(CTATXConfig[key]); };
//gradeStudent = window.parent.CTATXBlock.post.report_grade;

CTATLMS.identifier = 'XBlock';
CTATLMS.setValue = window.parent.CTATXBlock.post.set_variable;
CTATLMS.getValue = function(key) { return CTATXConfig[key]; };
CTATLMS.saveProblemState = function (state) {
    CTATLMS.setValue('saveandrestore',window.btoa(state));
};
CTATLMS.getProblemState = function (handler) {
    return handler(window.atob(CTATLMS.getValue('saveandrestore')));
};
CTATLMS.gradeStudent = window.parent.CTATXBlock.post.report_grade;
