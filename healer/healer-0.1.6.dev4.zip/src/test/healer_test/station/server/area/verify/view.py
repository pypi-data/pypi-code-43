"""
"""

from flask import Blueprint, render_template, url_for

blueprint = Blueprint('verify', __name__,
        static_folder='static',
        template_folder='template',
    )


@blueprint.route('/verify/main', methods=['GET'])
def ara_verify_main():
    return render_template('main.html', title='verify/main')
