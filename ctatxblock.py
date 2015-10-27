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
    href = String(help="URL to a BRD file", default="http://augustus.pslc.cs.cmu.edu/html5/HTML5TestFiles/1416-worked.brd", scope=Scope.content)
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
                </vertical_demo>
             """),
        ]
