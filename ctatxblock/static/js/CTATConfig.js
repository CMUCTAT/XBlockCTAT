/**
 * We prefabricate a set of flashvars such that the
 * loader can do things more naturally. It doesn't seem to be the case that
 * edX automatically makes an object that contains all these variables.
 * They have to be replaced by the python script when the XBlock html page is
 * generated.
 */

var CTATConfig = {{
   'admit_code': 'ies',
   authenticity_token: "",
   auth_token: "none",
   BehaviorRecorderMode: "AuthorTimeTutoring",
   class_name: "DefaultClass", // to replace with edx course code
   curriculum_service_url: "", // One of: 'OLI', 'SCORM', TutorShop url
   dataset_level_name: "none",
   dataset_level_type: "ProblemSet",
   dataset_name: "none",
   expire_logout_url: "none",
   instructor_name: "none",
   instrumentation_log: "off",
   lcId: "none",
   Logging: "ClientToService", // 'ClientToService' or 'ClientToLogServer', 'OLI'
   log_service_url: "http://pslc-qa.andrew.cmu.edu/log/server",
   problem_name: "none",
   problem_position: "none",
   problem_started_url: "none",
   //problem_state_status: "empty", //  'empty', 'complete', or 'incomplete'
   //question_file: "none",
   refresh_session_url: "none",
   //remoteSocketPort: "80",
   //remoteSocketURL: "127.0.0.1",
   restore_problem_url: "", // One of: 'OLI', 'SCORM', TutorShop url
   reuse_swf: "false",
   run_problem_url: "none",
   school_name: "none",
   SessionLog: "true",
   session_id: "none",
   session_timeout: "none",
   skills: "",
   source_id: "FLASH_PSEUDO_TUTOR", // 'FLASH_PSEUDO_TUTOR' or 'CTAT_JAVA_TUTOR'
   student_interface: "none",
   student_problem_id: "none",
   study_condition_name: "none",
   study_condition_type: "none",
   study_conditon_description: "none",
   study_name: "Study1",
   target_frame: "none",
   TutorShopDeliveryMethod: "sendandload",
   //user_guid: "none",
   wmode: "opaque",
   log_to_disk_directory: "none",
   DeliverUsingOLI: "none",
   ssl: "off",
   sui: "",

   'question_file': "{question_file}",
   //'DeliverUsingOLI': true, //unused
   'tutoring_service_communication': 'javascript',
   'user_guid': '{student_id}',
   //'baseUrl': null, // unused
   //'handlerBaseUrl': null, // unused
   //'href': null, // use 'question_file'
   //'module': null, // CTATXBlock
   'resource_spec': "{self.log_name}", // unsure if used
   //'problem': null, // unused
   //'src': null, // unused
   'dataset': "{self.log_dataset}",
   'level1': "{self.log_level1}",
   'type1': "{self.log_type1}",
   'level2': "{self.log_level2}",
   'type2': "{self.log_type2}",
   'logtype': "{self.logtype}",
   'distdir': "{self.log_diskdir}",
   'remoteSocketPort': {self.log_port},
   'remoteSocketURL': "{self.log_remoteurl}",
   'connection': "{self.ctat_connection}",

   'saveandrestore': "{self.saveandrestore}",
   'skills': "{self.skillstring}",
   'problem_state_status': "{self.completed}"!=="False"?'complete':"{self.saveandrestore}"!==""?'incomplete':'empty',
   //'restore_problem_url': 'OLI',
   'session_id': 'xblockstattutor_'+"{guid}"
}};