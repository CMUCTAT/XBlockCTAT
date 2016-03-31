# -------------------------------------------------------------------
#
#
# -------------------------------------------------------------------

import os
import pprint
import pkg_resources
import base64
import glob
import re
import socket
import uuid

from string import Template

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Float, Boolean, Any
from xblock.fragment import Fragment

dbgopen=False;
tmp_file=None;

# -------------------------------------------------------------------
#
#
# -------------------------------------------------------------------
class CTATXBlock(XBlock):
    """
    A XBlock providing CTAT tutors.
    """

    ### xBlock tag variables
    width = Integer(help="Width of the StatTutor frame.",
                    default=690, scope=Scope.content)
    height = Integer(help="Height of the StatTutor frame.",
                     default=550, scope=Scope.content)

    ### Grading variables
    has_score = Boolean(default=True, scope=Scope.content)
    icon_class = String(default="problem", scope=Scope.content)
    score = Integer(help="Current count of correctly completed student steps",
                    scope=Scope.user_state, default=0)
    max_problem_steps = Integer(
        help="Total number of steps",
        scope=Scope.user_state, default=1)
    def max_score(self):
        """ The maximum raw score of the problem. """
        return 1 #self.max_problem_steps
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
    ) # weight needs to be set to something

    ### Basic interface variables
    src = String(help="The source html file for CTAT interface.",
                 default="public/html/FractionAddition.html", scope=Scope.settings)
    brd = String(help="The behavior graph.",
                 default="public/problem_files/1416.brd",
                 scope=Scope.settings)

    ### CTATConfiguration variables
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

    ### user information
    saveandrestore = String(help="Internal data blob used by the tracer",
                            default="", scope=Scope.user_state)
    skillstring = String(help="Internal data blob used by the tracer",
                         default="", scope=Scope.user_info)

    def logdebug (self, aMessage):
        global dbgopen, tmp_file
        if (dbgopen==False):
            tmp_file = open("/tmp/edx-tmp-log-ctat.txt", "a", 0)
            dbgopen=True
        tmp_file.write (aMessage + "\n")

    def resource_string(self, path):
        """ Read in the contents of a resource file. """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def strip_local (self, url):
        """ Returns the given url with //localhost:port removed. """
        return re.sub('//localhost(:\d*)?', '', url)

    def get_local_resource_url (self, url):
        """ Wrapper for self.runtime.local_resource_url. """
        return self.strip_local(self.runtime.local_resource_url(self, url))

    # -------------------------------------------------------------------
    # TO-DO: change this view to display your data your own way.
    # -------------------------------------------------------------------

    def student_view(self, context=None):
        """
        Create a Fragment used to display a CTAT StatTutor xBlock to a student.

        Returns a Fragment object containing the HTML to display
        """
        # read in template html
        html = self.resource_string("static/html/ctatxblock.html")
        frag = Fragment (html.format(
            tutor_html=self.get_local_resource_url(self.src)))
        config = self.resource_string("static/js/CTATConfig.js")
        frag.add_javascript (config.format(
            self=self,
            tutor_html=self.get_local_resource_url(self.src),
            question_file=self.get_local_resource_url(self.brd),
            student_id=self.runtime.anonymous_student_id if hasattr(self.runtime, 'anonymous_student_id') else 'bogus-sdk-id',
            guid=str(uuid.uuid4())))
        frag.add_javascript (self.resource_string("static/js/Initialize_CTATXBlock.js"))
        frag.initialize_js('Initialize_CTATXBlock')
        return frag

    @XBlock.json_handler
    def ctat_grade(self, data, suffix=''):
        #self.logdebug ("ctat_grade ()")
        #print('ctat_grade:',data,suffix)
        self.attempted = True
        self.score = data['value']
        self.max_problem_steps = data['max_value']
        self.completed = self.score >= self.max_problem_steps
        scaled = self.score/self.max_problem_steps
        # trying with max of 1.
        event_data = {'value': scaled, 'max_value': 1}
        self.runtime.publish(self, 'grade', event_data)
        return {'result': 'success', 'state': self.completed}

    # -------------------------------------------------------------------
    # TO-DO: change this view to display your data your own way.
    # -------------------------------------------------------------------
    def studio_view(self, context=None):
        html = self.resource_string("static/html/ctatstudio.html")
        frag = Fragment(html.format(self=self))
        js = self.resource_string("static/js/ctatstudio.js")
        frag.add_javascript(unicode(js))
        frag.initialize_js('CTATXBlockStudio')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.src = data.get('src')
        self.brd = data.get('brd')
        self.width = data.get('width')
        self.height = data.get('height')
        return {'result': 'success'}

    @XBlock.json_handler
    def ctat_set_variable(self, data, suffix=''):
        self.logdebug ("ctat_set_variable ()")

        for key in data:
            #value = base64.b64decode(data[key])
            value = data[key]
            self.logdebug("Setting ({}) to ({})".format(key, value))
            if (key=="href"):
               self.href = value
            elif (key=="ctatmodule"):
               self.ctatmodule = value
            elif (key=="problem"):
               self.problem = value
            elif (key=="dataset"):
               self.dataset = value
            elif (key=="level1"):
               self.level1 = value
            elif (key=="type1"):
               self.type1 = value
            elif (key=="level2"):
               self.level2 = value
            elif (key=="type2"):
               self.type2 = value
            elif (key=="logurl"):
               self.logurl = value
            elif (key=="logtype"):
               self.logtype = value
            elif (key=="diskdir"):
               self.diskdir = value
            elif (key=="port"):
               self.port = value
            elif (key=="remoteurl"):
               self.remoteurl = value
            elif (key=="connection"):
               self.connection = value
            #elif (key=="src"):
            #   self.src = value
            elif (key=="saveandrestore"):
               self.logdebug ("Received saveandrestore request")
               self.saveandrestore = value
            #elif (key=="skillstring"):
            #  self.skillstring = value

        return {'result': 'success'}

    # -------------------------------------------------------------------
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    # -------------------------------------------------------------------
    @staticmethod
    def workbench_scenarios():
        return [
            ("CTATXBlock",
             """<vertical_demo>
                <ctatxblock width="" height=""/>
                </vertical_demo>
             """),
        ]
