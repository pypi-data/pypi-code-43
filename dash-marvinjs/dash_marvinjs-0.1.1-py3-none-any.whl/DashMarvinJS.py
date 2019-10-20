# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashMarvinJS(Component):
    """A DashMarvinJS component.


Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks.
- marvin_url (string; required): A URL of MarvinJS iframe.
- marvin_width (string; default '900'): Width of MarvinJS iframe.
- marvin_height (string; default '450'): Height of MarvinJS iframe.
- marvin_button (dict; default {
    'name' : 'Upload',
    'image-url' : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAArlBMVEUAAAAAAAA' +
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' +
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' +
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABeyFOlAAAAAXRSTlMAQObYZgAAAAFiS0' +
                  'dEAIgFHUgAAAAJcEhZcwAACcUAAAnFAYeExPQAAAAHdElNRQfjCQwVADLJ+C5eAAABUklEQVR42u3ZQWrDMBC' +
                  'F4TlMIFun2JD//hdLodBFLamWrMlL2jc7WWbmi2LkEY44FRsQulj4ClV9vkNdXyMArQC0AtAKQCsArQC0AtAK' +
                  'QCsArQC0AtAKQCsArQC0AtAKQCsArWBfojpIESz7AvVRhqCQvjGcD9gK2Vvj6YJS7uaFXECtLX8WoH4uSHwIC' +
                  'olpX1vTj2HFX5u3Eezzlpc7cTP+ua61/zth/V/zcGqAAQZkAY63ea25bbRZ7Ok06zMfzSzXevlLV69bnViGW2' +
                  'bmAH5Ncxvv/I8AtuFTwyTAgTT3KUfvEwDeFrDOeQjHASEGHN2IkgBrx1Z8GpDxMjLAAAMMMMAAAwwwwAADDDD' +
                  'AAAMMMODvAaLzO3EmIDSAGLt7IqDvO3EKoCcMMMAAAwwwwAADDDDAgPcCZIcBBrwmIP4RoLJTXNWAUNePuInr' +
                  'f8b92eUfelqXBAH/Tb4AAAAASUVORK5CYII=',
    'toolbar' : 'N'
}): Button config of MarvinJS iframe. marvin_button has the following type: dict containing keys 'name', 'image-url', 'toolbar'.
Those keys have the following types:
  - name (string; optional)
  - image-url (string; optional)
  - toolbar (string; optional)
- upload (string; optional): Storage for structure from backend
- download (string; optional): Storage for structure to backend"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, marvin_url=Component.REQUIRED, marvin_width=Component.UNDEFINED, marvin_height=Component.UNDEFINED, marvin_button=Component.UNDEFINED, upload=Component.UNDEFINED, download=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'marvin_url', 'marvin_width', 'marvin_height', 'marvin_button', 'upload', 'download']
        self._type = 'DashMarvinJS'
        self._namespace = 'dash_marvinjs'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'marvin_url', 'marvin_width', 'marvin_height', 'marvin_button', 'upload', 'download']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['marvin_url']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashMarvinJS, self).__init__(**args)
