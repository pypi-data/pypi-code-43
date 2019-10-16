
from django import forms


class AceEditorWidget(forms.Textarea):

    def __init__(self, mode=None, *args, **kwargs):
        self.mode = mode
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        js = [
            'medicine_utils/ace/ace.js',
            'medicine_utils/ace/ext-language_tools.js',
            'medicine_utils/ace/theme-twilight.js'
        ]

        if self.mode:
            js.append('medicine_utils/ace/mode-%s.js' % self.mode)

        css = {'screen': ['medicine_utils/ace/style.css']}

        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        id_name = attrs['id'].replace('-', '_')
        textarea = super().render(name, value, attrs, renderer)
        return (f'''
            {textarea}
            <div id="{attrs['id']}_editor" class="ace-editor"></div>
            <script>
            var textarea_{id_name} = django.jQuery("#{attrs['id']}").hide();
            var editor_{id_name} = ace.edit("{attrs['id']}_editor");
            editor_{id_name}.setTheme("ace/theme/twilight");
            editor_{id_name}.session.setMode("ace/mode/{self.mode}");
            editor_{id_name}.setOptions({{
                fontSize: '14px',
                minLines: 10,
                maxLines: Infinity,
                enableBasicAutocompletion: true
            }});
            editor_{id_name}.getSession().setValue(textarea_{id_name}.val());
            editor_{id_name}.getSession().on('change', function(){{
              textarea_{id_name}.val(editor_{id_name}.getSession().getValue());
            }});
            </script> 
            <style>
            .field-{name} {{
                margin: 0 -40px 0 -40px;
                padding: 20px 20px 20px 0;
                background: #232323;
            }}
            label[for="{attrs['id']}"] {{
                display: none;
            }}
            </style>
        ''')
