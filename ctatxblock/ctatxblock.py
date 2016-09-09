"""
A XBlock used to server CTAT based tutors.
See http://ctat.pact.cs.cmu.edu/ for more on CTAT tutors.
"""

import re
import uuid
import base64
import math
import pkg_resources

# pylint: disable=import-error
# The xBlock package are availabe in the runtime environment.
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Float, Boolean
from xblock.fragment import Fragment
#pylint: enable=import-error


class CTATXBlock(XBlock):
    """
    A XBlock providing CTAT tutors.
    """
    # pylint: disable=too-many-instance-attributes
    # All of the instance variables are required.

    display_name = String(
        help="Display name of the xBlock",
        default="CTAT Tutor",
        scope=Scope.content)
    # **** xBlock tag variables ****
    width = 690 #Integer(help="Width of the tutor frame.",
                #    default=690, scope=Scope.content)
    height = 550 #Integer(help="Height of the tutor frame.",
                 #    default=550, scope=Scope.content)

    # **** Grading variables ****
    # Required accordign to EdX's documentation in order to get grading to work
    has_score = Boolean(default=True, scope=Scope.content)
    icon_class = String(default="problem", scope=Scope.content)
    score = Integer(help="Current count of correctly completed student steps",
                    scope=Scope.user_state, default=0)
    max_problem_steps = Integer(
        help="Total number of steps",
        scope=Scope.user_state, default=1)
    max_possible_score = 1 # should this be 1.0?

    def max_score(self):
        """ The maximum raw score of the problem. """
        # For some unknown reason, errors are thrown if the return value is
        # hard coded.
        return self.max_possible_score
    attempted = Boolean(help="True if at least one step has been completed",
                        scope=Scope.user_state, default=False)
    completed = Boolean(
        help="True if all of the required steps are correctly completed",
        scope=Scope.user_state, default=False)
    weight = Float(
        display_name="Problem Weight",
        help=("Defines the number of points each problem is worth. "
              "If the value is not set, the problem is worth the sum of the "
              "option point values."),
        values={"min": 0, "step": .1},
        scope=Scope.settings
    )  # weight needs to be set to something, errors will be thrown if it does
    # not exist.


    # **** Basic interface variables ****
    src = String(help="The source html file for CTAT interface.",
                 #default="https://cdn.rawgit.com/CMUCTAT/CTAT/v4.0.0/Examples/FractionAddition.html",
                 #default="http://localhost/~mringenb/postMessage.html",
                 default="http://www.cs.cmu.edu/~mringenb/tutor/CTATNumberLine.html",
                 scope=Scope.settings)
    brd = String(help="The behavior graph.",
                 #default="https://cdn.rawgit.com/CMUCTAT/CTAT/v4.0.0/Examples/FractionAddition.brd",
                 default="http://www.cs.cmu.edu/~mringenb/tutor/CTATNumberLine.brd",
                 scope=Scope.settings)

    # **** CTATConfiguration variables ****
    # most of the addressing information should be available
    # from xblock.location (depreciated: xblock.id)
    log_name = String(help="Problem name to log", default="CTATEdXProblem",
                      scope=Scope.settings)
    log_dataset = String(help="Dataset name to log", default="edxdataset",
                         scope=Scope.settings)
    log_url = String(help="URL of the logging service",
                     default="http://pslc-qa.andrew.cmu.edu/log/server",
                     scope=Scope.settings)
    # None, ClientToService, ClientToLogServer, or OLI
    logtype = String(help="How should data be logged",
                     default="None", scope=Scope.settings)

    # **** User Information ****
    saveandrestore = String(help="Internal data blob used by the tracer",
                            default="", scope=Scope.user_state)
    skillstring = String(help="Internal data blob used by the tracer",
                         default="", scope=Scope.user_info)

    # **** Utility functions and methods ****
    @staticmethod
    def resource_string(path):
        """ Read in the contents of a resource file. """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @staticmethod
    def strip_local(url):
        """ Returns the given url with //localhost:port removed. """
        return re.sub(r'//localhost(:\d*)?', '', url)

    def get_local_resource_url(self, url):
        """ Wrapper for self.runtime.local_resource_url. """
        return self.strip_local(self.runtime.local_resource_url(self, url))

    # **** xBlock methods ****
    def student_view(self, dummy_context=None):
        """
        Create a Fragment used to display a CTAT xBlock to a student.

        Args:
          dummy_context: unused but required as a XBlock.student_view.
        Returns:
          a Fragment object containing the HTML to display.
        """
        # read in template html
        html = self.resource_string("static/html/ctatxblock.html")
        frag = Fragment(html.format(
            tutor_html=self.src, # FIXME: add ?mode=XBlock in such a way as to handle other get parameters
            width=self.width,
            height=self.height))
        config = self.resource_string("static/js/CTATConfig.js")
        frag.add_javascript(config.format(
            logtype=self.logtype,
            log_url=self.log_url,
            log_dataset=self.log_dataset,
            problem_name=self.log_name, #FIXME
            question_file=self.brd,
            student_id=self.runtime.anonymous_student_id
            if hasattr(self.runtime, 'anonymous_student_id')
            else 'bogus-sdk-id',
            saved_state=self.saveandrestore,
            skills=self.skillstring,
            completed=self.completed,
            usage_id=unicode(self.scope_ids.usage_id),
            # usage_id probably should be parsed. (example:
            # "block-v1:CMU+Stat001+2016+type@ctatxblock+block@ccd1ca4028e64467965c23d8ffbd1363")
            guid=str(uuid.uuid4())))
        frag.add_javascript(self.resource_string(
            "static/js/Initialize_CTATXBlock.js"))
        frag.initialize_js('Initialize_CTATXBlock')
        return frag

    @XBlock.json_handler
    def ctat_grade(self, data, dummy_suffix=''):
        """
        Handles updating the grade based on post request from the tutor.

        Args:
          self: the CTAT XBlock.
          data: A JSON object.
          dummy_suffix: unused but required as a XBlock.json_handler.
        Returns:
          A JSON object reporting the success or failure.
        """
        self.attempted = True
        corrects = 0
        if data.get('value') is not None:
            corrects = int(data.get('value'))
            if math.isnan(corrects): corrects = 0  # check for invalid value
        if data.get('max_value') is not None:
            max_val = int(data.get('max_value'))
            if not math.isnan(max_val) and max_val > 0:
                # only update if a valid number
                self.max_problem_steps = max_val
        # only change score if it increases.
        # this is done because corrects should only ever increase and
        # it deals with issues EdX has with grading, in particular
        # the multiple identical database entries issue.
        if corrects > self.score:
            self.score = corrects
            self.completed = self.score >= self.max_problem_steps
            scaled = float(self.score)/float(self.max_problem_steps)
            # trying with max of 1.
            event_data = {'value': scaled, 'max_value': 1.0}
            # pylint: disable=broad-except
            # The errors that should be checked are django errors, but there
            # type is not known at this point. This exception is designed
            # partially to learn what the possible errors are.
            try:
                self.runtime.publish(self, 'grade', event_data)
            except Exception as err:
                # return with the error message for debugging purposes.
                return {'result': 'fail', 'Error': err.message}
            return {'result': 'success', 'finished': self.completed,
                    'score': scaled}
            # pylint: enable=broad-except
        # report a no change situation (out of order or duplicate) with the
        # current score.
        return {'result': 'no-change', 'finished': self.completed,
                'score': float(self.score)/float(self.max_problem_steps)}

    def studio_view(self, dummy_context=None):
        """" Generate what is seen in the Studio view """
        html = self.resource_string("static/html/ctatstudio.html")
        frag = Fragment(html.format(self=self))
        studio_js = self.resource_string("static/js/ctatstudio.js")
        frag.add_javascript(unicode(studio_js))
        frag.initialize_js('CTATXBlockStudio')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, dummy_suffix=''):
        """
        Called when submitting the form in Studio.

        Args:
          self: the CTAT XBlock.
          data: a JSON object encoding the form data from
                static/html/ctatstudio.html
          dummy_suffix: unused but required as a XBlock.json_handler.
        Returns:
          A JSON object reporting the success of the operation.
        """
        if data.get('src') is not None:
            self.src = data.get('src')
        if data.get('brd') is not None:
            self.brd = data.get('brd')
        if data.get('width') is not None and not math.isnan(int(data.get('width'))):
            self.width = int(data.get('width'))
        if data.get('height') is not None and not math.isnan(int(data.get('height'))):
            self.height = int(data.get('height'))
        if data.get('dataset') is not None:
            self.log_dataset = data.get('dataset')
        if data.get('logtype') is not None:
            self.logtype = data.get('logtype')
        if data.get('logurl') is not None:
            self.log_url = data.get('logurl')
        return {'result': 'success'}

    @XBlock.json_handler
    def ctat_save_problem_state(self, data, dummy_suffix=''):
        """Called from CTATLMS.saveProblemState.
        This saves the current state of the tutor after each correct action.

        Args:
          self: the CTAT XBlock.
          data: A JSON object with a 'state' field with a payload of the blob
                of 64 bit encoded data that represents the current
                state of the tutor.
          dummy_suffix: unused but required as a XBlock.json_handler.
        Returns:
          A JSON object with a 'result' field with a payload indicating the
          success status.
        """
        if data.get('state') is not None:
            self.saveandrestore = data.get('state')
            return {'result': 'success'}
        return {'result': 'failure'}

    @XBlock.json_handler
    def ctat_save_skills(self, data, dummy_suffix=''):
        """Save the current skill estimates for the student.

        Args:
          self: the CTAT XBlock
          data: the JSON object with the encoded skill string
          dummy_suffix: unused but required as a XBlock.json_handler.
        Returns:
          A JSON object with a 'result' field with a payload indicating the
          success status.
        """
        # FIXME: actually insert hooks in code to send this.
        if data.get('skills') is not None:
            self.skillstring = data.get('skills')
            return {'result': 'success'}
        return {'result': 'failure'}

    @XBlock.json_handler
    def ctat_get_problem_state(self, dummy_data, dummy_suffix=''):
        """
        Return the stored problem state to reconstruct a student's progress.

        Args:
          self: the CTAT XBlock.
          dummy_data: unused but required as a XBlock.json_handler.
          dummy_suffix: unused but required as a XBlock.json_handler.
        Returns:
          A JSON object with a 'result' and a 'state' field.
        """
        return {'result': 'success', 'state': self.saveandrestore}

    @staticmethod
    def workbench_scenarios():
        """ Prescribed XBlock method for displaying this in the workbench. """
        return [
            ("CTATXBlock",
             """<vertical_demo>
                <ctatxblock width="" height=""/>
                </vertical_demo>
             """),
        ]
