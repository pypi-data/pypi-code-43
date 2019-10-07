import os.path
from pybars import Compiler
from .helpers import _header, _body, _footer

my_path = os.path.abspath(os.path.dirname(__file__))

simple = os.path.join(my_path, '../templates/simple.hbs')
alert = os.path.join(my_path, '../templates/alert.hbs')
notification = os.path.join(my_path, '../templates/notification.hbs')
information = os.path.join(my_path, '../templates/information.hbs')
table = os.path.join(my_path, '../templates/table.hbs')
list_template = os.path.join(my_path, '../templates/list_template.hbs')
button = os.path.join(my_path, '../templates/button.hbs')
textfield = os.path.join(my_path, '../templates/textfield.hbs')
checkbox = os.path.join(my_path, '../templates/checkbox.hbs')
textarea = os.path.join(my_path, '../templates/textarea.hbs')
radiobutton = os.path.join(my_path, '../templates/radiobutton.hbs')
personselector = os.path.join(my_path, '../templates/personselector.hbs')
dropdown_menu = os.path.join(my_path, '../templates/dropdown_menu.hbs')
table_select = os.path.join(my_path, '../templates/table_select.hbs')
form = os.path.join(my_path, '../templates/form.hbs')

compiler = Compiler()
helpers = {'header': _header, 'body': _body, 'footer': _footer}

smsTypes = dict(
     SIMPLE='simple',
     ALERT = 'alert',
     NOTIFICATION = 'notification',
     INFORMATION = 'information',
     TABLE = 'table',
     LIST_TEMPLATE = 'list_template',
     BUTTON = 'button',
     TEXTFIELD = 'textfield',
     CHECKBOX = 'checkbox',
     TEXTAREA = 'textarea',
     RADIOBUTTON = 'radiobutton',
     PERSONSELECTOR = 'personselector',
     DROPDOWN_MENU = 'dropdown_menu',
     TABLE_SELECT = 'table_select',
     FORM = 'form',
)

compiledTemplates = {}

def compile_templates():
    compiledTemplates[smsTypes['SIMPLE']] = open(simple).read()
    compiledTemplates[smsTypes['ALERT']] = open(alert).read()
    compiledTemplates[smsTypes['NOTIFICATION']] = open(notification).read()
    compiledTemplates[smsTypes['INFORMATION']] = open(information).read()
    compiledTemplates[smsTypes['TABLE']] = open(table).read()
    compiledTemplates[smsTypes['LIST_TEMPLATE']] = open(list_template).read()
    compiledTemplates[smsTypes['BUTTON']] = open(button).read()
    compiledTemplates[smsTypes['TEXTFIELD']] = open(textfield).read()
    compiledTemplates[smsTypes['CHECKBOX']] = open(checkbox).read()
    compiledTemplates[smsTypes['TEXTAREA']] = open(textarea).read()
    compiledTemplates[smsTypes['RADIOBUTTON']] = open(radiobutton).read()
    compiledTemplates[smsTypes['PERSONSELECTOR']] = open(personselector).read()
    compiledTemplates[smsTypes['DROPDOWN_MENU']] = open(dropdown_menu).read()
    compiledTemplates[smsTypes['TABLE_SELECT']] = open(table_select).read()
    compiledTemplates[smsTypes['FORM']] = open(form).read()

compile_templates()

def wrapByMessageMLTags(compiledMessage):
    return '<messageML>' + compiledMessage + '</messageML>'

def render(message, smsType):
    if not compiledTemplates[smsType]:
        compile_templates()
    if smsType == 'table_select':
        context = {'table' : message}
    elif smsType == 'form':
        context = {'message': message}
    else:
        context = {'message':message}
    template = compiler.compile(compiledTemplates[smsType])
    return template(context, helpers=helpers)

def renderInBot(message, smsType):
    compiledMessage = render(message, smsType)
    return compiledMessage

def renderInApp(message, smsType):
    compiledMessage = render(message, smsType)
    return wrapByMessageMLTags(compiledMessage)

def renderForm(message, smsType):
    form = ''
    elements = {'button': renderInBot,
                'textfield': renderInBot,
                'textarea': renderInBot,
                'checkbox': renderInBot,
                'radiobutton': renderInBot,
                'dropdown_menu': renderInBot,
                'personselector': renderInBot,
                'table_select': renderInBot}

    for dic in message['body']:
        for type, data in dic.items():
            form += elements[type](data, smsTypes[type.upper()])
    message['form'] = form
    compiledMessage = render(message, smsType)
    return compiledMessage
