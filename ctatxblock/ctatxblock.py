# -------------------------------------------------------------------
#
#
# -------------------------------------------------------------------

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

# -------------------------------------------------------------------
#
#
# -------------------------------------------------------------------
class CTATXBlock(XBlock):

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.
    href = String(help="URL to a BRD file", default="http://augustus.pslc.cs.cmu.edu/html5/", scope=Scope.settings)
    module = String(help="The learning module to load from", default="HTML5TestFiles", scope=Scope.settings)
    name = String(help="Problem name to log", default="CTATEdXProblem", scope=Scope.settings)	
    problem = String(help="The name of a BRD file", default="1416-worked.brd", scope=Scope.settings)
    dataset = String(help="Dataset name to log", default="edxdataset", scope=Scope.settings)
    level1 = String(help="Level name to log", default="unit1", scope=Scope.settings)
    type1 = String(help="Level type to log", default="unit", scope=Scope.settings)
    level2 = String(help="Level name to log", default="unit2", scope=Scope.settings)
    type2 = String(help="Level type to log", default="unit", scope=Scope.settings)
    logurl = String(help="URL of the logging service", default="http://pslc-qa.andrew.cmu.edu/log/server", scope=Scope.settings)
    logtype = String(help="How should data be logged", default="clienttologserver", scope=Scope.settings)
    diskdir = String(help="Directory for log files relative to the tutoring service", default=".", scope=Scope.settings)
    port = String(help="Port used by the tutoring service", default="8080", scope=Scope.settings)
    remoteurl = String(help="Location of the tutoring service (localhost or domain name)", default="localhost", scope=Scope.settings)
    connection = String(help="", default="javascript", scope=Scope.settings)

    src = String(help = "URL for MP3 file to play", scope = Scope.settings )	
	
    def resource_string(self, path):
        data = pkg_resources.resource_string(__name__, path)        
        return data.decode("utf8")

    # -------------------------------------------------------------------
    # TO-DO: change this view to display your data your own way.
    # -------------------------------------------------------------------

    def student_view(self, context=None):
        html = self.resource_string("static/html/ctatxblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/ctat.css"))
        frag.add_css(self.resource_string("static/css/ctatxblock.css"))
        frag.add_javascript(self.resource_string("static/js/ctat.min.js"))
        frag.add_javascript(self.resource_string("static/js/ctatloader.js"))
        frag.initialize_js('CTATXBlock')
        return frag

#    def student_view(self, context=None):
#        html = self.resource_string("static/html/ctatstudio.html")
#        frag = Fragment(html.format(src=self.src))
#        frag.add_css(self.resource_string("static/css/ctatstudio.css"))
#        frag.initialize_js('CTATXBlock')
#        return frag
    
    # -------------------------------------------------------------------
    # TO-DO: change this view to display your data your own way.
    # -------------------------------------------------------------------
    def studio_view(self, context=None):        
        html = self.resource_string("static/html/ctatstudio.html")
        frag = Fragment(html.format(src=self.src))
        frag.add_css(self.resource_string("static/css/ctatstudio.css"))
        frag.initialize_js('CTATXBlock')        
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        self.src = data.get('src')
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
                <ctatxblock/>
                </vertical_demo>
             """),
        ]
