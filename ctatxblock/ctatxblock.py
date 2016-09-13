"""
A XBlock used to server CTAT based tutors.
See http://ctat.pact.cs.cmu.edu/ for more on CTAT tutors.
"""

import re
import uuid
# import base64
import math
import json
import pkg_resources
import requests
import bleach

# pylint: disable=import-error
# The xBlock package are availabe in the runtime environment.
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Float, Boolean
from xblock.fragment import Fragment
# pylint: enable=import-error


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
    # Required accordign to EdX's documentation in order to get grading to work
    has_score = Boolean(default=True, scope=Scope.content)
    icon_class = String(default="problem", scope=Scope.content)
    score = Integer(help="Current count of correctly completed student steps",
                    scope=Scope.user_state, default=0)
    max_problem_steps = Integer(
        help="Total number of steps",
        scope=Scope.user_state, default=1)
    max_possible_score = 1  # should this be 1.0?

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
                 # default="https://cdn.rawgit.com/CMUCTAT/CTAT/v4.0.0" +
                 # "/Examples/FractionAddition.html",
                 default="http://www.cs.cmu.edu/~mringenb/tutor/CTATNumberLine.html",
                 scope=Scope.settings)
    brd = String(help="The behavior graph.",
                 # default="https://cdn.rawgit.com/CMUCTAT/CTAT/v4.0.0" +
                 # "/Examples/FractionAddition.brd",
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

    custom_tutor_parameters = String(
        help="Extra parameters set by the author for the tutor. " +
        "This should be JSON code. See https://github.com/CMUCTAT/CTAT/" +
        "wiki/Advanced-Topics#tutor-configuration.",
        default="{}",
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

    # **** xBlock methods ****
    def student_view(self, dummy_context=None):
        """
        Create a Fragment used to display a CTAT xBlock to a student.

        Args:
          dummy_context: unused but required as a XBlock.student_view.
        Returns:
          a Fragment object containing the HTML to display.
        """
        # pylint: disable=broad-except
        # There are a fair number of exceptions raised by raise_for_status
        # and all of them are handled the same way here.
        try:
            # See if tutor interface is reachable and add mode parameter
            tutor = requests.get(self.src, params={'mode': 'XBlock'})
            tutor.raise_for_status()
        except Exception as err:
            # Return a Fragment with the error message so that authors can
            # get some relevant information as to why the tutor is not loading.
            return Fragment((u'<p style="width:{width}px;height:{height}px;' +
                             'border:2px solid red;">Error retrieving ' +
                             'specified tutor {url} ({error})</p>').format(
                                 url=self.src,
                                 error=err,
                                 height=self.height,
                                 width=self.width))
        # pylint: enable=broad-except
        # read in template html
        html = self.resource_string("static/html/ctatxblock.html")
        # fill in the template html
        frag = Fragment(html.format(
            tutor_html=tutor.url,
            width=self.width,
            height=self.height))
        # read in the template js
        config = self.resource_string("static/js/CTATConfig.js")
        # fill in the js template
        frag.add_javascript(config.format(
            logtype=self.logtype,
            log_url=self.log_url,
            log_dataset=self.log_dataset,
            problem_name=self.log_name,  # FIXME
            question_file=self.brd,
            student_id=self.runtime.anonymous_student_id
            if hasattr(self.runtime, 'anonymous_student_id')
            else 'bogus-sdk-id',  # conditional here in case testing in sdk
            saved_state=self.saveandrestore,
            skills=self.skillstring,
            completed=self.completed,
            usage_id=unicode(self.scope_ids.usage_id),
            # usage_id probably should be parsed. (example:
            # "block-v1:CMU+Stat001+2016+type@ctatxblock+block@ccd1ca4028e64467965c23d8ffbd1363")
            guid=str(uuid.uuid4())))
        # Add javascript initialization code
        frag.add_javascript(self.resource_string(
            "static/js/Initialize_CTATXBlock.js"))
        # Execute javascript initialization code
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
        try:
            if data.get('value') is not None:
                corrects = int(data.get('value'))
                if math.isnan(corrects):
                    corrects = 0  # check for invalid value
            if data.get('max_value') is not None:
                max_val = int(data.get('max_value'))
                if not math.isnan(max_val) and max_val > 0:
                    # only update if a valid number
                    self.max_problem_steps = max_val
        except ValueError as int_err:
            return {'result': 'fail', 'error': unicode(int_err)}
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
                return {'result': 'fail', 'error': unicode(err)}
            return {'result': 'success', 'finished': self.completed,
                    'score': scaled}
            # pylint: enable=broad-except
        # report a no change situation (out of order or duplicate) with the
        # current score.
        return {'result': 'no-change', 'finished': self.completed,
                'score': float(self.score)/float(self.max_problem_steps)}

    def studio_view(self, dummy_context=None):
        """" Generate what is seen in the Studio view Edit dialogue. """
        # read in template
        html = self.resource_string("static/html/ctatstudio.html")
        # Make fragment and fill out template
        frag = Fragment(html.format(
            src=self.src,
            brd=self.brd,
            width=self.width,
            height=self.height,
            log_url=self.log_url,
            dataset=self.log_dataset,
            log_name=self.log_name,
            custom=self.custom_tutor_parameters,
            logging='checked' if self.logtype == "ClientToService" else ''))
        # read in, add, and execute javascript
        studio_js = self.resource_string("static/js/ctatstudio.js")
        frag.add_javascript(unicode(studio_js))
        frag.initialize_js('CTATXBlockStudio')
        return frag

    @staticmethod
    def validate_interface(url):
        """ Validate that the passed url is a CTAT tutor interface. """
        if url is None:
            raise Exception('No html interface file specified.')
        src = bleach.clean(url.strip(), strip=True)
        tutor = requests.get(src, params={'mode': 'XBlock'})
        tutor.raise_for_status()
        if tutor.headers['Content-Type'] != 'text/html':
            raise Exception(src + ' does not appear to be a text/html file.')
        if not re.search(r'ctat\.min\.js', tutor.text, re.I):
            raise Exception(src + ' does not appear to be a CTAT interface.')
        return src

    @staticmethod
    def validate_brd(url):
        """ Validate that the passed url is a CTAT BRD file. """
        if url is None:
            raise Exception('No BRD file specified.')
        brd = bleach.clean(url.strip(), strip=True)
        tutor = requests.get(brd)
        tutor.raise_for_status()
        if not re.search(r'<stateGraph', tutor.text):
            raise Exception(brd + ' does not appear to be a proper BRD file.')
        return brd

    @staticmethod
    def validate_number(num, default):
        """ Validate that the passed string is a number. """
        if num is None:
            return default
        return int(num)

    @staticmethod
    def validate_logging(enable_logging):
        """Validate that the string is a proper value for enabling logging."""
        logging = "None"
        if enable_logging is not None:
            logging = bleach.clean(enable_logging, strip=True)
            if logging.lower() == "true":
                logging = "ClientToService"
        return logging

    @staticmethod
    def validate_log_param(data, param, logging, default):
        """ Validate the given logging parameter if logging is enabled. """
        log_param = default
        if data.get(param) is not None:
            log_param = bleach.clean(data.get(param), strip=True)
        if logging != "None":
            if len(log_param) <= 0:
                raise Exception('No specified ' + param +
                                ' when logging is enabled.')
        return log_param

    @staticmethod
    def validate_custom(json_string):
        """ Validate that the string is JSON. """
        custom = ''
        if json_string is not None:
            # bleach the string
            custom = bleach.clean(json_string, strip=True)
            # attempt to parse it as json to see if it is valid.
            # relying on this to raise a ValueError if not proper json.
            json.loads(custom)
        return custom

    @XBlock.json_handler
    def studio_submit(self, data, dummy_suffix=''):
        """
        Called when submitting the form in Studio.
        This will only modify values if all of the safty checks pass.

        Args:
          self: the CTAT XBlock.
          data: a JSON object encoding the form data from
                static/html/ctatstudio.html
          dummy_suffix: unused but required as a XBlock.json_handler.
        Returns:
          A JSON object reporting the success of the operation.
        """
        # pylint: disable=broad-except
        # This uses the generic exceptions so that we do not have to
        # generate custom error classes and this handles the classes
        # of exceptions potentially raised by requests
        try:
            valid_src = self.validate_interface(data.get('src'))
            valid_brd = self.validate_brd(data.get('brd'))
            valid_width = self.validate_number(data.get('width'), self.width)
            valid_height = self.validate_number(data.get('height'),
                                                self.height)
            valid_logtype = self.validate_logging(data.get('logging'))
            valid_log_url = self.validate_log_param(data, 'logserver',
                                                    valid_logtype,
                                                    self.log_url)
            valid_log_dataset = self.validate_log_param(data, 'dataset',
                                                        valid_logtype,
                                                        self.log_dataset)
            valid_log_name = self.validate_log_param(data, 'problemname',
                                                     valid_logtype,
                                                     self.log_name)
            valid_custom = self.validate_custom(data.get('custom'))
        except Exception as err:
            return {'result': 'fail', 'error': unicode(err)}
        # pylint: enable=broad-except
        # Only update values if all checks pass
        self.src = valid_src
        self.brd = valid_brd
        self.width = valid_width
        self.height = valid_height
        self.logtype = valid_logtype
        self.log_url = valid_log_url
        self.log_dataset = valid_log_dataset
        self.log_name = valid_log_name
        self.custom_tutor_parameters = valid_custom
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
            self.saveandrestore = bleach.clean(data.get('state'))
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
            self.skillstring = bleach.clean(data.get('skills'), strip=True)
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
                <ctatxblock width="690" height="550"/>
                </vertical_demo>
             """),
        ]
