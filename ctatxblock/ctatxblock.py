"""
A XBlock used to server CTAT based tutors.
"""

import re
import uuid
import pkg_resources

# pylint: disable=import-error
# The xBlock package are availabe in the runtime environment.
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Float, Boolean
from xblock.fragment import Fragment


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
    width = Integer(help="Width of the tutor frame.",
                    default=690, scope=Scope.content)
    height = Integer(help="Height of the tutor frame.",
                     default=550, scope=Scope.content)

    # **** Grading variables ****
    has_score = Boolean(default=True, scope=Scope.content)
    icon_class = String(default="problem", scope=Scope.content)
    score = Integer(help="Current count of correctly completed student steps",
                    scope=Scope.user_state, default=0)
    max_problem_steps = Integer(
        help="Total number of steps",
        scope=Scope.user_state, default=1)
    max_possible_score = 1

    def max_score(self):
        """ The maximum raw score of the problem. """
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
    )  # weight needs to be set to something

    # **** Basic interface variables ****
    src = String(help="The source html file for CTAT interface.",
                 default="public/html/FractionAddition.html",
                 scope=Scope.settings)
    brd = String(help="The behavior graph.",
                 default="public/problem_files/1416.brd",
                 scope=Scope.settings)

    # **** CTATConfiguration variables ****
    # most of the addressing information should be available
    # from xblock.location (depreciated: xblock.id)
    log_name = String(help="Problem name to log", default="CTATEdXProblem",
                      scope=Scope.settings)
    log_dataset = String(help="Dataset name to log", default="edxdataset",
                         scope=Scope.settings)
    log_level1 = String(help="Level name to log", default="unit1",
                        scope=Scope.settings)
    log_type1 = String(help="Level type to log", default="unit",
                       scope=Scope.settings)
    log_level2 = String(help="Level name to log", default="unit2",
                        scope=Scope.settings)
    log_type2 = String(help="Level type to log", default="unit",
                       scope=Scope.settings)
    log_url = String(help="URL of the logging service",
                     default="http://pslc-qa.andrew.cmu.edu/log/server",
                     scope=Scope.settings)
    logtype = String(help="How should data be logged",
                     default="clienttologserver", scope=Scope.settings)
    log_diskdir = String(
        help="Directory for log files relative to the tutoring service",
        default=".", scope=Scope.settings)
    log_port = String(help="Port used by the tutoring service", default="8080",
                      scope=Scope.settings)
    log_remoteurl = String(
        help="Location of the tutoring service (localhost or domain name)",
        default="localhost", scope=Scope.settings)

    ctat_connection = String(help="", default="javascript",
                             scope=Scope.settings)

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

        Returns a Fragment object containing the HTML to display
        """
        # read in template html
        html = self.resource_string("static/html/ctatxblock.html")
        frag = Fragment(html.format(
            tutor_html=self.get_local_resource_url(self.src),
            width=self.width,
            height=self.height))
        config = self.resource_string("static/js/CTATConfig.js")
        frag.add_javascript(config.format(
            self=self,
            tutor_html=self.get_local_resource_url(self.src),
            question_file=self.get_local_resource_url(self.brd),
            student_id=self.runtime.anonymous_student_id
            if hasattr(self.runtime, 'anonymous_student_id')
            else 'bogus-sdk-id',
            course_id=unicode(self.scope_ids.usage_id),
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
        """
        self.attempted = True
        corrects = int(data.get('value'))
        self.max_problem_steps = int(data.get('max_value'))
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
        """
        self.src = data.get('src')
        self.brd = data.get('brd')
        self.width = data.get('width')
        self.height = data.get('height')
        return {'result': 'success'}

    @XBlock.json_handler
    def ctat_save_problem_state(self, data, dummy_suffix=''):
        """Called from CTATLMS.saveProblemState."""
        if data.get('state') is not None:
            self.saveandrestore = data.get('state')
            return {'result': 'success'}
        return {'result': 'failure'}

    @XBlock.json_handler
    def ctat_get_problem_state(self, dummy_data, dummy_suffix=''):
        """
        Return the stored problem state to reconstruct a student's progress.
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
