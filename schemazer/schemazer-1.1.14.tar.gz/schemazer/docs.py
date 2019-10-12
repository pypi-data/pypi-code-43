from flask import Blueprint, abort, current_app, json, render_template

doc_bp = Blueprint(
    'doc', __name__,
    template_folder='./templates',
    static_folder='static',
    static_url_path='/static/doc'
)

base_params = {
    'project_name': current_app.schemazer.config.PROJECT_NAME,
    'docs_path': current_app.schemazer.config.DOCS_PATH
}


def _schema_groups():
    return [x for x in dir(current_app.schemazer.schema)
            if not x.startswith('_')]


def _errors():
    groups = current_app.schemazer.schema.__groups__
    errors = set()

    for group in groups:
        for method in group().__methods__:
            errors.update(set(method.errors))

    return errors


@doc_bp.route(f'/{current_app.schemazer.config.DOCS_PATH}/')
def documentation():
    groups = [x.__group_name__ for x in
              current_app.schemazer.schema.__groups__]
    groups.sort()

    params = {
        'version': current_app.schemazer.config.VERSION,
        'groups': groups,
    }
    params.update(base_params)

    return render_template('pages/index.html', **params)


@doc_bp.route(f'/{current_app.schemazer.config.DOCS_PATH}/methods/',
              methods=['GET'])
def method_groups():
    groups = [x for x in dir(current_app.schemazer.schema)
              if not x.startswith('_')]
    groups.sort()

    params = {
        'title': 'Methods api',
        'host_ip': current_app.schemazer.config.HOST,
        'groups': groups,
    }
    params.update(base_params)

    return render_template('pages/groups.html', **params)


@doc_bp.route(
    f'/{current_app.schemazer.config.DOCS_PATH}/methods/<string:group>/',
    methods=['GET'])
def method_for_group(group):
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

    return render_template('pages/methods.html', **params)


@doc_bp.route(
    f'/{current_app.schemazer.config.DOCS_PATH}/methods/'
    f'<string:group>.<string:method>/',
    methods=['GET'])
def method_route(group, method):
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

    return render_template('pages/method.html', **params)


@doc_bp.route(f'/{current_app.schemazer.config.DOCS_PATH}/errors/',
              methods=['GET'])
def errors_route():
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

    return render_template('pages/errors.html', **params)


@doc_bp.route(
    f'/{current_app.schemazer.config.DOCS_PATH}/errors/'
    f'<string:error_group>.<string:error_name>/',
    methods=['GET'])
def error_route(error_group, error_name):
    find_error = None
    for error in _errors():
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

    return render_template('pages/error.html', **params)
