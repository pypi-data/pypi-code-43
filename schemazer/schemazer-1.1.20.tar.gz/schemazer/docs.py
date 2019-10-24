from functools import wraps
from flask import (
    Blueprint, abort, current_app, json, render_template,
    request, make_response, redirect)

doc_bp = Blueprint(
    'doc', __name__,
    template_folder='./templates',
    static_folder='static',
    static_url_path='/static/doc'
)

base_params = {
    'project_name': current_app.schemazer.config.PROJECT_NAME,
    'docs_path': current_app.schemazer.config.DOCUMENTATION_PATH
}


def _all_errors_in_schema():
    groups = current_app.schemazer.schema.__groups__
    errors = set()

    for group in groups:
        for method in group().__methods__:
            errors.update(set(method.errors))

    return errors


def check_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get(
            current_app.schemazer.config.AUTH_COOKIE_PARAMETER)

        if token == current_app.schemazer.config.AUTH_ACCESS_TOKEN:
            response = func(*args, **kwargs)
            response.set_cookie(
                current_app.schemazer.config.AUTH_COOKIE_PARAMETER,
                token, max_age=60*60)
            return response
        else:
            return redirect(
                current_app.schemazer.config.DOCUMENTATION_LOGIN_PAGE_PATH)

    return wrapper


@doc_bp.route(current_app.schemazer.config.DOCUMENTATION_PATH)
@check_access
def route_index():
    groups = [x.__group_name__ for x in
              current_app.schemazer.schema.__groups__]
    groups.sort()

    params = {
        'version': current_app.schemazer.config.VERSION,
        'groups': groups,
        'error_code': current_app.schemazer.config.ERROR_HTTP_CODE,
    }
    params.update(base_params)

    rs = make_response(render_template('pages/index.html', **params))

    return rs


@doc_bp.route(
    f'{current_app.schemazer.config.DOCUMENTATION_PATH}/methods/',
    methods=['GET'])
@check_access
def route_all_groups():
    groups = [x for x in dir(current_app.schemazer.schema)
              if not x.startswith('_')]
    groups.sort()

    params = {
        'title': 'Methods api',
        'host_ip': current_app.schemazer.config.HOST,
        'groups': groups,
    }
    params.update(base_params)

    return make_response(render_template('pages/groups.html', **params))


@doc_bp.route(
    f'{current_app.schemazer.config.DOCUMENTATION_PATH}/'
    f'methods/<string:group>/',
    methods=['GET'])
@check_access
def route_group_of_methods(group):
    group_obj = getattr(current_app.schemazer.schema, group, None)

    if not group_obj:
        abort(404)

    methods = [x for x in dir(group_obj) if not x.startswith('_')]
    methods.sort()

    params = {
        'title': 'SchemazerMethod group %s' % group,
        'host_ip': current_app.schemazer.config.HOST,
        'group': group,
        'methods': methods,
    }
    params.update(base_params)

    return make_response(render_template('pages/methods.html', **params))


@doc_bp.route(
    f'{current_app.schemazer.config.DOCUMENTATION_PATH}/methods/'
    f'<string:group>.<string:method>/',
    methods=['GET'])
@check_access
def route_method(group, method):
    group_obj = getattr(current_app.schemazer.schema, group, None)

    if not group_obj or not getattr(group_obj, method, None):
        abort(404)

    method_schema = getattr(group_obj, method, None)

    response = {
        'schema': json.dumps(
            method_schema.response.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False)
    }

    if method_schema.response:
        response['example'] = json.dumps(
            method_schema.response.example,
            indent=2,
            sort_keys=True,
            ensure_ascii=False
        )

    params = {
        'title': f'{group}.{method_schema.name}',
        'host_ip': current_app.schemazer.config.HOST,
        'group': group,
        'method': method,
        'method_schema': method_schema,
        'response': response,
        'errors': [x.to_dict() for x in method_schema.errors],
    }
    params.update(base_params)

    return make_response(render_template('pages/method.html', **params))


@doc_bp.route(
    f'{current_app.schemazer.config.DOCUMENTATION_PATH}/errors/',
    methods=['GET'])
@check_access
def route_all_errors():
    groups = current_app.schemazer.schema.__groups__
    errors = set()

    for group in groups:
        for method in group().__methods__:
            errors.update(set(method.errors))

    errors_repr = [error.to_dict() for error in errors]
    errors_list = sorted(errors_repr, key=lambda k: k['code'])

    params = {
        'title': 'Errors',
        'errors': errors_list or [],
    }
    params.update(base_params)

    return make_response(render_template('pages/errors.html', **params))


@doc_bp.route(
    f'{current_app.schemazer.config.DOCUMENTATION_PATH}/errors/'
    f'<string:error_group>.<string:error_name>/',
    methods=['GET'])
@check_access
def route_error(error_group, error_name):
    find_error = None
    for error in _all_errors_in_schema():
        if error.code == f'{error_group}.{error_name}':
            find_error = error
            break

    if not find_error:
        abort(404)

    params = {
        'title': 'Ошибка %s' % find_error.code,
        'error': find_error,
    }
    params.update(base_params)

    return make_response(render_template('pages/error.html', **params))


@doc_bp.route(
    current_app.schemazer.config.DOCUMENTATION_LOGIN_PAGE_PATH,
    methods=['GET']
)
def route_login():
    return make_response(render_template(
        'pages/login.html',
        msg=request.args.get('msg', ''),
        action=current_app.schemazer.config.DOCUMENTATION_LOGIN_PAGE_PATH,
        **base_params
    ))


@doc_bp.route(
    current_app.schemazer.config.DOCUMENTATION_LOGIN_PAGE_PATH,
    methods=['POST'])
def route_login_post():
    pwd = request.form.get('password')
    login = request.form.get('login')

    if (current_app.schemazer.config.AUTH_LOGIN != login or
            current_app.schemazer.config.AUTH_PWD != pwd):
        return redirect(
            f'{current_app.schemazer.config.DOCUMENTATION_LOGIN_PAGE_PATH}?'
            f'msg=error')

    response = redirect(current_app.schemazer.config.DOCUMENTATION_PATH)
    response.set_cookie(
        current_app.schemazer.config.AUTH_COOKIE_PARAMETER,
        current_app.schemazer.config.AUTH_ACCESS_TOKEN,
        max_age=current_app.schemazer.config.AUTH_COOKIE_TTL
    )

    return response


@doc_bp.route(
    current_app.schemazer.config.DOCUMENTATION_LOGOUT_PAGE_PATH,
    methods=['GET'])
def route_logout():
    response = redirect(
        current_app.schemazer.config.DOCUMENTATION_LOGIN_PAGE_PATH)
    response.set_cookie(
        current_app.schemazer.config.AUTH_COOKIE_PARAMETER, None)

    return response
