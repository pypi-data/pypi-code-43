#
# Copyright (c) 2010, 2014, 2015, 2017, 2018
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
# THE SOFTWARE
#
import time
from yaml.parser import ParserError
from coils.core import \
    PropertyManager, \
    get_yaml_struct_from_project7000, \
    CoilsException

TASK_RULES_CACHED_YAML = dict()
TASK_RULES_CACHED_ETAG = 0


def get_task_rules(context, task):

    global TASK_RULES_CACHED_YAML
    global TASK_RULES_CACHED_ETAG

    if task.kind is None:
        context.log.debug(
            'Task rules not processed for tasks without kind, OGo#{0}'
            .format(task.object_id, )
        )
        return None

    ruleset, etag, = TASK_RULES_CACHED_YAML.get(task.kind, (None, None, ))

    if (etag is None) or (etag < time.time()):
        """
        Attempt to load ruleset for task kind for first time or after expiry
        """
        try:
            ruleset = get_yaml_struct_from_project7000(
                context,
                'Rules/Tasks/{0}.yaml'.format(task.kind, ),
                access_check=False,
            )
        except ParserError as exc:
            context.log.exception(exc)
            context.log.error(
                'YAML expression of rules for task kind "{0}" is invalid'
                .format(task.kind, )
            )
            ruleset = None
        except CoilsException as exc:
            context.log.exception(exc)
            ruleset = None
            context.log.debug(
                'No task rules loaded for tasks of kind "{0}"'
                .format(task.kind, )
            )
        else:
            context.log.debug(
                'Task ruleset loaded for tasks of kind "{0}"'
                .format(task.kind, )
            )
        finally:
            TASK_RULES_CACHED_YAML[task.kind] = (ruleset, time.time() + 90.0, )
            if not ruleset:
                context.log.debug(
                    'Task ruleset for tasks of kind "{0}" is empty'
                    .format(task.kind, )
                )

    return ruleset


def get_task_key_value(context, task, key):
    if key.startswith('{'):
        namespace, attribute = PropertyManager.Parse_Property_Name(key)
        prop = context.property_manager.get_property(
            entity=task,
            namespace=namespace,
            attribute=attribute,
        )
        if not prop:
            return False
        return prop.get_value()
    else:
        if hasattr(task, key):
            return getattr(task, key)
    return None


def task_matches_rule(context, task, rule):

    for match_rule in rule['match']:

        key_name = match_rule.get('key')
        value = match_rule.get('value')
        expression = match_rule.get('expression', 'EQUALS')

        if not compare_rule_value_to_value(
            context=context, task=task,
            key=key_name,
            value=value,
            expression=expression,
        ):
            context.log.debug(
                '({0}[{1}] {2} {3}) is False'
                .format(
                    key_name,
                    get_task_key_value(context, task, key_name, ),
                    expression,
                    value,
                )
            )
            break
    else:
        return True
    return False


def apply_rule_to_task(context, task, rule):

    for apply_rule in rule['apply']:
        key = apply_rule.get('key')
        value = apply_rule.get('value')
        if key.startswith('{'):
            """ Set value of specified object property """
            namespace, attribute, = PropertyManager.Parse_Property_Name(key)
            context.property_manager.set_property(
                entity=task,
                namespace=namespace,
                attribute=attribute,
                value=value,
            )
            """ Record rule action in audit log """
            context.audit_at_commit(
                object_id=task.object_id,
                action='10_commented',
                message=(
                    'Task property {0} set to "{1}" by rule "{2}".'
                    .format(
                        key,
                        value,
                        rule.get('name', 'unnamed'),
                    )
                ),
                version=task.version,
            )
        else:
            if hasattr(task, key):
                """ Record rule action in audit log """
                context.audit_at_commit(
                    object_id=task.object_id,
                    action='10_commented',
                    message=(
                        'Task attribute {0} changed '
                        'from "{1}" to "{2}" by rule {3}.'
                        .format(
                            key,
                            getattr(task, key),
                            value,
                            rule.get('name', 'unnamed'),
                        )
                    ),
                    version=task.version,
                )
                setattr(task, key, value)
            else:
                """ Record rule failure in audit log """
                context.audit_at_commit(
                    object_id=task.object_id,
                    action='10_commented',
                    message=(
                        'Rule "{0}" cannot change value of unknown '
                        'attribute "{1}" to "{2}"'
                        .format(
                            rule.get('name', 'unnamed'),
                            key,
                            value,
                        )
                    ),
                    version=task.version,
                )

    if 'action' in rule:
        context.run_command(
            'task::comment',
            task=task,
            process_rules=False,
            values={
                'action': rule['action'],
                'comment': (
                    'Action performed by rule "{0}"'
                    .format(rule.get('name', 'unnamed'), )
                ),
            },
        )

    if 'link' in rule:
        for link in rule:
            try:
                target_id = int(link.get('target', None))
                description = link.get('description', None)
                kind = link.get('kind', 'generic')
            except:
                # TODO: log warning/error
                continue
            else:
                target_id = None
            if target_id:
                target = context.type_manager.get_entity(target_id)
                if not target:
                    # TODO: log warning/error
                    continue
                context.link_manager.link(
                    task, target, kind=kind, label=description,
                )


def compare_rule_value_memberof(context, task_value, rule_value):
    if not isinstance(task_value, int):
        return False
    if not isinstance(rule_value, int):
        return False
    ctxids = context.run_command('account::get-context-ids', id=task_value, )
    return (rule_value in ctxids)


def compare_rule_value_to_value(
    context, task, key, value, expression='EQUALS',
):
    compare_value = get_task_key_value(context, task, key)

    if expression == 'EQUALS':
        return (compare_value == value)
    if expression == 'ISNULL':
        return (compare_value is None)
    if expression == 'ISNOTNULL':
        return not (compare_value is None)
    if expression == 'NOTEQUALS':
        return not(compare_value == value)
    if expression == 'IN':
        return (compare_value in value)
    if expression == 'NOTIN':
        return not(compare_value in value)
    if expression == 'MEMBEROF':
        return compare_rule_value_memberof(context, compare_value, value)
    if expression == 'NOTMEMBEROF':
        return not compare_rule_value_memberof(context, compare_value, value)

    raise CoilsException(
        'Invalid expresion in rule match declaration; '
        'must be one of EQUALS, NOTEQUALS, ISNULL, ISNOTNULL, '
        'MEMBEROF, IN, or NOTIN.'
    )


class TaskCommand(object):

    def verify_values(self):
        # TODO: Verify parent_id is a task
        # TODO: Verify project_id is a project
        # TODO: Verify creator is an account
        # TODO: Verify owner is a contact
        # TODO: Verify priority
        # TODO: Verify sensitivity
        # TODO: Verify % complete
        # TODO: Verify start > now
        # TODO: Verify end > start
        if self.obj.parent_id:
            # task cannot be a parent of itself
            if self.obj.parent_id == self.obj.object_id:
                raise CoilsException('Task cannot be a parent of itself')
            # verify parent task exists
            tmp = self.get_by_id(self.obj.parent_id, False)
            if not tmp:
                raise CoilsException(
                    'Cannot marshal parent_id value "{0}" as task'
                    .format(self.obj.parent_id, )
                )
            # simple loop detection
            if tmp.parent_id:
                if tmp.parent_id == self.obj.object_id:
                    raise CoilsException(
                        'Parent task loop detected with OGo#{0}'
                        .format(tmp.object_id, )
                    )
            tmp = None

        return True

    def get_by_id(self, object_id, access_check):
        task = self._ctx.run_command(
            'task::get', id=object_id,
            access_check=access_check,
        )
        return task

    def do_tko(self):
        pass

    def sanitize_values(self):
        '''
        Protect against wierd values and NULL/NOT-NULL issues
        '''
        if self.obj.parent_id == 0:
            self.obj.parent_id = None

        if self.obj.project_id == 0:
            self.obj.project_id = None

        if self.obj.kind == '':
            self.obj.kind = None

        # Control status of the job.is_team_job field.
        if self._ctx.type_manager.get_type(self.obj.executor_id) == 'Team':
            self.obj.team_job = 1
        elif self.obj.team_job is None:
            self.obj.team_job = 0

        # Legacy likes these values to be empty strings, not NULL
        if self.obj.category is None:
            self.obj.category = ''
        if self.obj.associated_companies is None:
            self.obj.associated_companies = ''
        if self.obj.associated_contacts is None:
            self.obj.associated_contacts = ''

    def process_attachments(self):
        '''
        We only attempt to process attachments if the incoming value is a
        dict - that being an Omphalos representation (possibly created
        from a vTODO).
        '''
        if isinstance(self.values, dict):
            if '_ATTACHMENTS' in self.values:
                '''
                First loaded with all attachments keyed, by checksum.  Then
                matching attachments [already exist] will be eliminated
                leaving just the attachments that need to be created.
                '''
                attachments_ = {}
                '''
                Will be populated with attachment UUIDs that need to be deleted
                '''
                deletes_ = []
                for attachment_ in self.values['_ATTACHMENTS']:
                    hash_ = attachment_.get('sha512checksum', None)
                    if hash_:
                        attachments_[hash_] = attachment_

                # Pivot from the enumeration of existing attachments
                for attachment in self.obj.attachments:
                    if attachment.checksum in attachments_:
                        # Attachment already exists; potentially change name?
                        name_ = attachments_[attachment.checksum]['name']
                        attachment.webdav_uid = \
                            name_ if name_ else attachment.webdav_uid
                        '''
                        Delete from dict, nothing more needs to be done with it
                        '''
                        del attachments_[attachment.checksum]
                    else:
                        '''
                        The attachment does not exist in the list of provided
                        attachments
                        '''
                        deletes_.append(attachment.uuid)
                '''
                Loop the attachments that remain in the dict, creating new
                attachment entities.
                '''
                for attachment_ in attachments_.values():
                    if 'data' in attachment_:
                        '''
                        TODO: If the mimetype is 'application/octet-stream
                        *and* we have a name, try to guess a mimetype from the
                        file extension
                        '''
                        self._ctx.run_command(
                            'attachment::new',
                            data=attachment_['data'],
                            name=attachment_['name'],
                            related_id=self.obj.object_id,
                            mimetype=attachment_['mimetype'],
                        )
                '''
                Delete the attachment entities we no longer find in the
                object representation
                '''
                for uuid_ in deletes_:
                    self._ctx.run_command('attachment::delete', uuid=uuid_)

    def apply_rules(self):
        """
        Apply task rules to the task.  This should always be last step
        performed on the task by the Logic command; create or update. It
        is expected that the values have already been verified and sanatized.
        """

        ruleset = get_task_rules(context=self._ctx, task=self.obj)

        if not ruleset:
            # No rules to process
            return

        for rule in ruleset:
            if task_matches_rule(context=self._ctx, task=self.obj, rule=rule):
                apply_rule_to_task(context=self._ctx, task=self.obj, rule=rule)
                self.log.debug(
                    'Task rule "{0}" applied to task OGo#{1}'
                    .format(rule.get('name', 'unnamed'), self.obj.object_id, )
                )
            else:
                self.log.debug(
                    'Task rule "{0}" does not apply to task OGo#{1}'
                    .format(rule.get('name', 'unnamed'), self.obj.object_id, )
                )
