
# Copyright (c) 2015
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from pprint import pformat
from yaml.parser import ParserError
import traceback

from coils.core import \
    NoSuchPathException, \
    get_yaml_struct_from_project7000, \
    CoilsException


from coils.net import PathObject, StaticObject


class TaskRuleDemo(PathObject):
    """
    For testing of task rulesets

    URI paramters:
        objectId
        taskId - presense inidcates that an e-mail should be sent
        floorSeconds - age of events to be included, default is ~1 year
        floorObjectId  - what the object id floor is for included events
    """

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def is_public(self):
        return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        if not hasattr(self, 'ruleset'):
            """
            We are loading a ruleset by name
            """
            try:
                ruleset = get_yaml_struct_from_project7000(
                    self.context,
                    'Rules/Tasks/{0}.yaml'.format(name, ),
                    access_check=False,
                )
            except ParserError:
                return StaticObject(
                    self, name,
                    context=self.context,
                    request=self.request,
                    parameters=self.parameters,
                    mimetype='text/plain',
                    payload=(
                        'YAML expression of rules for task kind "{0}" '
                        'is invalid.\n{1}\n'.format(
                            name,
                            traceback.format_exc(),
                        )
                    )
                )
            except CoilsException:
                return StaticObject(
                    self, name,
                    context=self.context,
                    request=self.request,
                    parameters=self.parameters,
                    mimetype='text/plain',
                    payload=(
                        'No task rules loaded for task kind "{0}" \n{1}\n'
                        .format(
                            name,
                            traceback.format_exc(),
                        )
                    )
                )

            return TaskRuleDemo(
                self, name,
                context=self.context,
                request=self.request,
                parameters=self.parameters,
                ruleset=ruleset
            )

        task_id = long(name)
        task = self.context.run_command('task::get', id=task_id, )
        if not task:
            raise NoSuchPathException(
                'Unable to marshall task OGo#{0}'.format(task_id, )
            )
        return TaskRuleDemo(
            self, name,
            context=self.context,
            request=self.request,
            parameters=self.parameters,
            ruleset=self.ruleset,
            task=task,
        )

    def do_GET(self):

        if hasattr(self, 'task'):
            from coils.logic.task.command import task_matches_rule
            result = list()
            for rule in self.ruleset:
                if task_matches_rule(self.context, self.task, rule):
                    result.append(
                        'Task matches rule "{0}"'
                        .format(rule.get('name', 'unnamed'), )
                    )
                else:
                    result.append(
                        'Task does not match rule "{0}"'
                        .format(rule.get('name', 'unnamed'), )
                    )
            self.request.simple_response(
                200,
                mimetype='text/plain',
                data='\n'.join(result),
            )
            return

        if hasattr(self, 'ruleset'):
            self.request.simple_response(
                200,
                mimetype='text/plain',
                data=pformat(self.ruleset),
            )
            return

        self.request.simple_response(
            200,
            mimetype='text/plain',
            data='/toolbox/taskrule/KIND or /toolbox/taskrule/KIND/TASKID',
        )
