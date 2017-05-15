#
# Copyright 2017 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from ecs.ecsHelper import ecsHelper

print "Create ECS Service"

ecsHelper = ecsHelper(deployed)

taskDefinition = "%s:%s" % (deployed.family, deployed.revision)
print "Task Definition    : %s" % (taskDefinition)
print "Cluster            : %s" % (deployed.container.name)
print "Service Name       : %s" % (deployed.serviceName)
print "Number of Tasks    : %s" % (deployed.desiredCount)
print "Min Healthy Percent: %s" % (deployed.minimumHealthyPercent)
print "Maximum Percent    : %s" % (deployed.maximumPercent)
print "LoadBalancer       : %s" % (deployed.loadbalancerName)

oneLB = { 'loadBalancerName': deployed.loadbalancerName,
          'containerPort': deployed.containerDefinitions[0].portMappings[0].containerPort}
print oneLB


response = ecsHelper.createService(deployed, taskDefinition )
print "========================================="
print response
print "========================================="
print "Done ECS Service"

