from enum import Enum
import json
import time

from fabnodes.lib import stack


class Actions(Enum):
    CREATE = 'create'
    REVIEW = 'review'
    CFNDSL = 'cfndsl'
    JINJA = 'jinja'
    YAML = 'yaml'
    DELETE = 'delete'
    UPDATE = 'update'
    PURGE = 'purge'
    MAKE_DIST = 'makedist'
    PUSH_DIST = 'pushdist'
    TEST_FEATURE = 'testfeature'

    @classmethod
    def to_list(cls):
        return [x.lower() for x, _ in cls.__members__.items()]


def _create_bucket(appconf, node, rendered_template):
    if(
            not stack._validate_template(appconf, node, rendered_template) or
            not stack._create_stack(appconf, node, rendered_template) or
            not stack._wait_for_stack_state(
                appconf, 'CREATE_IN_PROGRESS', 'CREATE_COMPLETE')):
        return False
    return True


def _create(appconf, node, rendered_template):
    if(appconf['template_file'] == 'code_bucket.rb.j2'):
        return _create_bucket(appconf, node, rendered_template)
    if(
            not stack._validate_template(appconf, node, rendered_template) or
            not stack._clean_temp_files(appconf) or
            not stack._create_distribution_environment() or
            not stack._install_requirements() or
            not stack._make_zip(appconf) or
            not stack._upload_dist(appconf) or
            not stack._clean_temp_files(appconf) or
            not stack._create_stack(appconf, node, rendered_template) or
            not stack._wait_for_stack_state(
                appconf, 'CREATE_IN_PROGRESS', 'CREATE_COMPLETE')):
        return False
    return True


def _delete(appconf):
    if(
            not stack._delete_stack(appconf) or
            not stack._wait_for_stack_state(
                appconf, 'DELETE_IN_PROGRESS', 'DELETE_COMPLETE')):
        return False
    return True


def _cfndsl(appconf, node, rendered_template):
    if rendered_template:
        return rendered_template
    return False


def _review(appconf, node, rendered_template):
    template = stack._gen_from_template(appconf, node, rendered_template)
    if not template:
        return False
    return json.dumps(json.loads(template), indent=4, sort_keys=True)


def _create_dist(appconf):
    if(
            not stack._clean_temp_files(appconf) or
            not stack._create_distribution_environment() or
            not stack._install_requirements() or
            not stack._make_zip(appconf)):
        return False
    return True


def _push_dist(appconf):
    if(
            not stack._upload_dist(appconf)):
        return False
    return True


def _does_template_apply(template, action):
    if template == 'cfndsl.rb.j2':
        return True
    if template == 'code_bucket.rb.j2':
        return action not in [Actions.MAKE_DIST, Actions.PUSH_DIST]
    return False


def execute_action(act, appconf, path, template):
    ret = False
    out = []
    start = time.time()
    if not _does_template_apply(appconf['template_file'], act):
        out.append('Skipping')
        return True, out
    if act == Actions.CREATE:
        with open(path, 'r') as node_f:
            ret = _create(appconf, node_f, template)
    elif act == Actions.REVIEW:
        with open(path, 'r') as node_f:
            result = _review(appconf, node_f, template)
            if result:
                ret = True
                out.append(result)
    elif act == Actions.CFNDSL:
        with open(path, 'r') as node_f:
            result = _cfndsl(appconf, node_f, template)
            if result:
                ret = True
                out.append(result)
    elif act == Actions.JINJA:
        out.append('Unimplemented action')
    elif act == Actions.DELETE:
        ret = _delete(appconf)
    elif act == Actions.MAKE_DIST:
        ret = _create_dist(appconf)
    elif act == Actions.PUSH_DIST:
        ret = _push_dist(appconf)
    else:
        out.append('Unimplemented action')
    end = time.time()

    if act != Actions.REVIEW:
        out.append('Elapsed time: %f seconds' % (end - start))
    return ret, out
