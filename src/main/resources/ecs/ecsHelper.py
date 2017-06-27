#
# Copyright 2017 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import commons
from boto3.session import Session
from botocore.session import Session as BotocoreSession


class ecsHelper(object):
    def __init__(self, deployed, deployed_application=None):
        self.deployed = deployed
        self.deployed_application = deployed_application

        botocore_session = BotocoreSession()
        botocore_session.lazy_register_component('data_loader',
                                                 lambda: commons.create_loader())

        if deployed.container.type == "aws.Cloud":
            aws_keys_container = deployed.container
        else:
            aws_keys_container = deployed.container.AwsKeys

        self.session = Session(aws_access_key_id=aws_keys_container.accesskey,
                               aws_secret_access_key=aws_keys_container.accessSecret,
                               botocore_session=botocore_session)

        if hasattr(self.deployed, 'region') and self.deployed.region is not None:
            self.ecs_client = self.session.client('ecs', region_name=self.deployed.region, use_ssl=True, verify=False)

    def ecs_containers(self):
        ecs_containers = []
        for container in self.deployed.containerDefinitions:
            ecs_container = {}
            ecs_container['name'] = container.name
            ecs_container['image'] = container.image
            ecs_container['memory'] = container.memory
            if container.essential == "true":
                ecs_container['essential'] = True
            else:
                ecs_container['essential'] = False

            ecs_container['environment'] = []
            for key in container.environment:
                entry = {}
                value = container.environment[key]
                entry['name'] = key
                entry['value'] = value
                ecs_container['environment'].append(entry)

            # ecs_container['volumesFrom'] = container.volumesFrom
            # ecs_container['hostname'] = container.hostname
            # ecs_container['user'] = container.user
            # ecs_container['workingDirectory'] = container.workingDirectory
            # ecs_container['extraHosts'] = container.extraHosts
            # ecs_container['logConfiguration'] = container.logConfiguration
            # ecs_container['ulimits'] = container.ulimits
            # ecs_container['dockerLabels'] = container.dockerLabels
            port_mappings = []
            for port in container.portMappings:
                port_mappings.append(
                    {'containerPort': port.containerPort, 'hostPort': port.hostPort, 'protocol': port.protocol})

            if len(port_mappings) > 0:
                ecs_container['port_mappings'] = port_mappings

            mount_points = []
            for mount in container.mountPoints:
                mount_points.append({'sourceVolume': mount.sourceVolume, 'containerPath': mount.containerPath,
                                     'readOnly': mount.readOnly})

            if len(mount_points) > 0:
                ecs_container['mount_point'] = mount_points

            ecs_containers.append(ecs_container)

        return ecs_containers

    def find_task_definition(self, task_definition_name):
        print "find_task_definition {0}".format(task_definition_name)
        result = [deployed for deployed in self.deployed_application.deployeds if
                  deployed.type == "aws.ecs.TaskDefinition" and deployed.name == task_definition_name]

        if len(result) == 0:
            raise Exception("task definition {0} not found".format(task_definition_name))

        if len(result) > 1:
            raise Exception(
                "too many results [{1}] found for task definition {0} ".format(task_definition_name, len(result)))

        return result[0]

    def register_task_definition(self):
        container_definitions = self.ecs_containers()
        response = self.ecs_client.register_task_definition(family=self.deployed.family,
                                                            networkMode=self.deployed.networkMode,
                                                            taskRoleArn=self.deployed.taskRoleArn,
                                                            placementConstraints=self.deployed.placementConstraints or [],
                                                            volumes=self.deployed.volumes,
                                                            containerDefinitions=container_definitions)
        self.deployed.revision = response['taskDefinition']['revision']
        return response

    def run_task(self):
        task_definition = self.task_definition()
        print "Run task using {0} task definition.".format(task_definition)
        response = self.ecs_client.run_task(cluster=self.cluster(),
                                            taskDefinition=self.task_definition(),
                                            count=self.deployed.taskCount
                                            )
        if len(response['failures']) > 0:
            print "Error(s) found"
            for failure in response['failures']:
                print "{arn} => {reason}".format(**failure)
                raise Exception('ERROR run task %s' % (self.task_definition()))

        task_ids = []
        for task in response['tasks']:
            print "{taskArn}  {lastStatus} -> {desiredStatus}".format(**task)
            task_ids.append(task['taskArn'])

        self.deployed.taskIds = task_ids
        print self.deployed.taskIds

        return response

    def stop_task(self):
        if len(self.deployed.taskIds) == 0:
            raise Exception('No taskIds found in the deployed ')

        for task in self.deployed.taskIds:
            print "stop {0} from {1}".format(task, self.cluster())
            self.ecs_client.stop_task(cluster=self.cluster(),
                                      task=task,
                                      reason="XL DEPLOY",
                                      )

    def check_for_tasks_get_desired_status(self):
        nb_tasks = len(self.deployed.taskIds)
        response = self.ecs_client.describe_tasks(cluster=self.cluster(),
                                                  tasks=self.deployed.taskIds)
        desired_tasks = 0
        for task in response['tasks']:
            print "{taskArn}/{lastStatus}/{desiredStatus}".format(**task)
            if task['lastStatus'] == task['desiredStatus']:
                desired_tasks = desired_tasks + 1

        return desired_tasks, nb_tasks

    def deregister_task_definition(self):
        response = self.ecs_client.deregister_task_definition(taskDefinition=self.task_definition())
        return response

    def task_definition(self):
        if self.deployed.type == "aws.ecs.Task":
            task_definition_name = self.deployed.taskDefinitionName
            task_definition = self.find_task_definition(task_definition_name)
        else:
            task_definition = self.deployed

        return "{0}:{1}".format(task_definition.family, task_definition.revision)

    def cluster(self):
        return self.deployed.container.name

    def createService(self, deployed, taskDefinition, container_name, container_port):
        oneLB = {'loadBalancerName': deployed.loadbalancerName,
                 'containerName': container_name,
                 'containerPort': container_port}

        print oneLB
        loadBalancers = [oneLB]
        response = self.ecs_client.create_service(cluster=deployed.container.name,
                                                  serviceName=deployed.serviceName,
                                                  taskDefinition=taskDefinition,
                                                  loadBalancers=loadBalancers,
                                                  role=deployed.role,
                                                  desiredCount=deployed.desiredCount)
        return response

    def deleteService(self, previousDeployed, taskDefinition):
        response = self.ecs_client.update_service(cluster=previousDeployed.container.name,
                                                  service=previousDeployed.serviceName,
                                                  desiredCount=0,
                                                  taskDefinition=taskDefinition)
        print response
        response = self.ecs_client.delete_service(cluster=previousDeployed.container.name,
                                                  service=previousDeployed.serviceName)
        return response
