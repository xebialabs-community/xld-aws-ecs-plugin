#
# Copyright 2017 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from ecs.ecsHelper import ecsHelper

print "Register Task Definition ECS Task {0}".format(deployed.name)

deployed.placementConstraints = []
deployed.taskRoleArn = ""
deployed.volumes = []
ecsHelper = ecsHelper(deployed)

print "volumes : %s" % (deployed.volumes)
print "networkMode : %s" % (deployed.networkMode)
print "placementConstraints : %s" % (deployed.placementConstraints)
print "family               : %s" % (deployed.family)
print "task Name            : %s" % (deployed.name)
print "taskRoleArn          : %s" % (deployed.taskRoleArn)


response = ecsHelper.register_task_definition()
print "====================="
print response
print "Done ECS Task"
