""" REST JSON API

:Author: Mike Zheng <xzheng20@colby.edu>
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2019-07-03
:Copyright: 2019, Karr Lab
:License: MIT
"""

import bcforms
import bcforms.core
import bpforms
from wc_utils.util.chem import EmpiricalFormula
import flask
import flask_restplus
import flask_restplus.errors
import flask_restplus.fields

# the max total length of bpforms-encoded subunits must be less than 50
max_len_get_structure = 50

# setup app
app = flask.Flask(__name__)


class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')

api = flask_restplus.Api(app,
                         title='bcforms JSON REST API',
                         description='JSON REST API for calculating properties of biocomplex forms',
                         contact='info@karrlab.org',
                         version=bcforms.__version__,
                         license='MIT',
                         license_url='https://github.com/KarrLab/bcforms/blob/master/LICENSE',
                         doc='/')

bcform_ns = flask_restplus.Namespace('bcform', description='Calculate properties of biocomplex forms')
api.add_namespace(bcform_ns)

# define model

# if encoding, structure defined -> ignore formula, mol_wt, charge, and define them based on structure
# if neither encoding, structure set and formula is defined -> ignore mol_wt, and define mol_wt based on formula
subunit_fields = {}
subunit_fields['name'] = flask_restplus.fields.String(required=True, title='Subunit name', example='abc_a')
# encoding can be smiles, bpforms.ProteinForm, bpforms.DnaForm, bpforms.RnaForm
subunit_fields['encoding'] = flask_restplus.fields.String(required=False, title='Structure encoding', example='bpforms.ProteinForm')
subunit_fields['structure'] = flask_restplus.fields.String(required=False, title='Structure string', example='AAA')
subunit_fields['formula'] = flask_restplus.fields.String(required=False, title='Empirical formula', example='C5H10O')
subunit_fields['mol_wt'] = flask_restplus.fields.Float(required=False, title='Molecular weight', example=86.0)
subunit_fields['charge'] = flask_restplus.fields.Integer(required=False, title='Total charge', example=0)

bcform_fields = {}
bcform_fields['form'] = flask_restplus.fields.String(required=True, title='BcForm', description='input biocomplex form', example='2 * abc_a + 3 * abc_b')
bcform_fields['subunits'] = flask_restplus.fields.List(flask_restplus.fields.Nested(bcform_ns.model('Subunit',subunit_fields)), example=[
    {
      "name": "abc_a",
      "encoding": "bpforms.ProteinForm",
      "structure": "AAA"
    },
    {
      "name": "abc_b",
      "encoding": "bpforms.ProteinForm",
      "structure": "MM"
    }
  ])

bcforms_model = bcform_ns.model('BcForm', bcform_fields)


@bcform_ns.route("/")
class Bcform(flask_restplus.Resource):

    @bcform_ns.expect(bcforms_model, validate=True)
    def post(self):
        ret = {}
        warnings = []

        args = bcform_ns.payload

        # print(args)

        # get arguments
        form = args['form']
        arg_subunits = args.get('subunits', None)

        # validate form
        try:
            bc_form = bcforms.core.BcForm().from_str(form)
        except Exception as error:
            flask_restplus.abort(400, 'Form is invalid', errors={'form': str(error)})

        errors = bc_form.validate()
        if errors:
            flask_restplus.abort(400, 'Form is invalid', errors={'form': '. '.join(errors)})

        # validate input subunit properties
        sum_length = 0
        if arg_subunits is not None:
            for subunit in arg_subunits:

                # check if name is in the form
                subunit_id = subunit['name']
                if subunit_id in [subunit.id for subunit in bc_form.subunits]:

                    # check if encoding and structure are present at the same time
                    if ('encoding' in subunit) and ('structure' in subunit):
                        # if encoding and structure both present, check if encoding is known
                        encoding = subunit['encoding'].strip()
                        if encoding == 'bpforms.ProteinForm':
                            try:
                                subunit_structure = bpforms.ProteinForm().from_str(subunit['structure'])
                                sum_length += len(subunit_structure) * bc_form.get_subunit_attribute(subunit_id, 'stoichiometry')
                                bc_form.set_subunit_attribute(subunit_id, 'structure', subunit_structure)
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse bpforms.ProteinForm', errors={'structure': str(error)})
                        elif encoding == 'bpforms.DnaForm':
                            try:
                                subunit_structure = bpforms.DnaForm().from_str(subunit['structure'])
                                sum_length += len(subunit_structure) * bc_form.get_subunit_attribute(subunit_id, 'stoichiometry')
                                bc_form.set_subunit_attribute(subunit_id, 'structure', subunit_structure)
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse bpforms.DnaForm', errors={'structure': str(error)})
                        elif encoding == 'bpforms.RnaForm':
                            try:
                                subunit_structure = bpforms.RnaForm().from_str(subunit['structure'])
                                sum_length += len(subunit_structure) * bc_form.get_subunit_attribute(subunit_id, 'stoichiometry')
                                bc_form.set_subunit_attribute(subunit_id, 'structure', subunit_structure)
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse bpforms.RnaForm', errors={'structure': str(error)})
                        elif encoding == 'smiles' or encoding == 'SMILES' or encoding == 'smi' or encoding == 'SMI':
                            try:
                                bc_form.set_subunit_attribute(subunit_id, 'structure', subunit['structure'])
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse SMILES string', errors={'structure': str(error)})

                    # else if one is present but not the other, report error
                    elif ('encoding' in subunit) ^ ('structure' in subunit):
                        flask_restplus.abort(400, 'One of encoding and structure is present but not both')

                    # when neither encoding nor structure is present
                    else:
                        # check formula
                        if 'formula' in subunit:
                            try:
                                bc_form.set_subunit_attribute(subunit_id, 'formula', subunit['formula'])
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse formula', errors={'formula': str(error)})
                        elif 'mol_wt' in subunit:
                            try:
                                bc_form.set_subunit_attribute(subunit_id, 'mol_wt', subunit['mol_wt'])
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse mol_wt', errors={'mol_wt': str(error)})

                        # check charge
                        if 'charge' in subunit:
                            try:
                                bc_form.set_subunit_attribute(subunit_id, 'charge', subunit['charge'])
                            except Exception as error:
                                flask_restplus.abort(400, 'Unable to parse charge', errors={'charge': str(error)})

                else:
                    flask_restplus.abort(400, 'Subunit name not in BcForm', errors={'subunit':subunit_id})


        ret['form'] = str(bc_form)

        if sum_length <= max_len_get_structure:
            try:
                ret['structure'] = bc_form.export()
            except Exception:
                pass
        else:
            warnings.append('The sum of length of bpforms-encoded subunits is {}, which exceeds the max length limit {}.'.format(sum_length, max_len_get_structure))
            ret['structure'] = None

        try:
            ret['formula'] = str(bc_form.get_formula())
        except Exception:
            pass

        try:
            ret['mol_wt'] = bc_form.get_mol_wt()
        except Exception:
            pass

        try:
            ret['charge'] = bc_form.get_charge()
        except Exception:
            pass

        if len(warnings) > 0:
            ret['warnings'] = ' '.join(warnings)

        return ret

xlink_ns = flask_restplus.Namespace('crosslink', description='List crosslinks and get information about crosslinks')
api.add_namespace(xlink_ns)

@xlink_ns.route("/")
@xlink_ns.doc(params={})

class CrosslinkResource(flask_restplus.Resource):
    """ Get crosslinks """

    def get(self):
        """ Get crosslinks

        Returns:
            :obj:`dict`: dictionary representation of all crosslinks
        """
        return get_crosslinks()


@bcforms.core.cache.memoize(typed=False, expire=30 * 24 * 60 * 60)
def get_crosslinks():
    """ Get an alphabet

    Returns:
        :obj:`dict`: dictionary representation of crosslinks
    """

    crosslink_dict = dict(bcforms.core.parse_yaml(bcforms.core._xlink_filename))

    return crosslink_dict

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
