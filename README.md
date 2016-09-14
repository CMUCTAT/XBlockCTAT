# CTAT Tutors XBlock

This is the basic [XBlock](https://github.com/edx/XBlock) framework
used to deploy tutors developed using the
[Cognitive Tutor Authoring Tools](http://ctat.pact.cs.cmu.edu)
from [Carnegie Mellon University](http://www.cmu.edu/).

Cognitive Tutors have been successful in raising students' math test
scores in high school and middle-school classrooms, but their
development has traditionally required considerable time and
expertise. With the Cognitive Tutor Authoring Tools (CTAT), creating
Cognitive Tutors is both easier for experts and possible for novices
in cognitive science. The tools draw on ideas of programming by
demonstration, structured editing, and others.

## Installation

The steps to install all XBlocks can be found on
[edX's XBlocks integration page](https://github.com/edx/edx-documentation/blob/master/en_us/developers/source/extending_platform/xblocks.rst#testing).
Follow the instructions outlined in the `Testing` section if you're running
the devstack or scroll down to those outlined under
`Deploying your XBlock` if you're not.

## How to Configure

Once the XBlock is installed, use Studio to add tutors to a course by
navigating to a unit and clicking on `Advanced` and then on
`ctatxblock`. To change which tutor is deployed, click on `Edit` and
use the text inputs to specify the url to the html interface file and the brd
file.  These files need to be hosted on a web server accessable by your users and
use CTAT version 4.1.0 or greater.
There are additional spaces for specifying the size of the
tutor, logging information, and advanced configuration options.
