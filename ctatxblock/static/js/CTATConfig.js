/**
 * We prefabricate a set of flashvars such that the
 * loader can do things more naturally. It doesn't seem to be the case that
 * edX automatically makes an object that contains all these variables.
 * They have to be replaced by the python script when the XBlock html page is
 * generated.
 */

var CTATConfig = {{
    // meta
    'session_id': 'xblockctat_'+"{guid}",
    'user_guid': '{student_id}',

    // class
    'class_name': "{course}",
    'school_name': "{org}",
    'period_name': "{run}",
    'class_description': 'EdX class',

    // dataset
    'dataset_name': "{course_key}",
    'problem_name': "{problem_name}",
    'dataset_level_name1': "{block_type}",
    'dataset_level_type1': "Unit",

    'problem_context': "{tutor_html}: {question_file}",

    // runtime
    'connection': "javascript",
    // if window.$$course_id is undefined, then this is in an environment
    // that should forcibly disable logging (eg) in Studio or in the SDK
    'Logging': window.$$course_id?("{logtype}"=="True"?"ClientToService":"None"):"None",
    'Logging': "{logtype}"=="True"?"ClientToService":"None",
    'log_service_url': "edx://localhost",

    'question_file': "{question_file}", // BRD information
    'tutoring_service_communication': 'javascript',

    'saveandrestore': "{saved_state}",
    'skills': "{skills}",
    'problem_state_status': "{completed}"!=="False"?'complete':"{saved_state}"!==""?'incomplete':'empty',
}};

try {{
    var custom_params = JSON.parse('{custom}');
    CTATConfig = Object.assign(CTATConfig, custom_params);
}} catch(err) {{
    console.log('Invalid JSON in custom parameters: ' + err);
}}
