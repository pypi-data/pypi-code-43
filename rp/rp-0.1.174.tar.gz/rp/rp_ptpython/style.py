from __future__ import unicode_literals

def get_all_ui_styles():
    """
    Return a dict mapping {ui_style_name -> style_dict}.
    """
    return {
        'default': default_ui_style,
        'blue': blue_ui_style,
        # 'inverted_1': inverted_1,
        'lightning': inverted_2,
        'stars': inverted_3,
        'cyan': cyan,
        'aqua': cyan_2,
        'blew':cyan_3,
        'seashell':cyan_4,
        'jojo':color_1,
        'bizarre':color_2,
        'adventure':color_3,
        'pupper':pupper,
        'clara':clara,
        'emma':emma,
    }

from pygments.token import Token, Keyword, Name, Comment, String, Operator, Number
from pygments.styles import get_style_by_name, get_all_styles
from rp.prompt_toolkit.styles import DEFAULT_STYLE_EXTENSIONS, style_from_dict
from rp.prompt_toolkit.utils import is_windows, is_conemu_ansi

__all__ = (
    'get_all_code_styles',
    'get_all_ui_styles',
    'generate_style',
)


def get_all_code_styles():
    """
    Return a mapping from style names to their classes.
    """
    result = dict((name, get_style_by_name(name).styles) for name in get_all_styles())
    # from rp import mini_terminal_for_pythonista
    # exec(mini_terminal_for_pythonista)
    result['win32'] = win32_code_style
    result['ryan']=ryan_style
    return result
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Punctuation, Generic, Whitespace
"""
The style used in Lovelace interactive learning environment. Tries to avoid
the "angry fruit salad" effect with desaturated and dim colours.
"""
_KW_BLUE='#2838b0'
_NAME_GREEN='#388038'
_DOC_ORANGE='#b85820'
_OW_PURPLE='#a848a8'
_FUN_BROWN='#785840'
_STR_RED='#b83838'
_CLS_CYAN='#287088'
_ESCAPE_LIME='#709030'
_LABEL_CYAN='#289870'
_EXCEPT_YELLOW='#908828'
ryan_style={Token: '',
            Token.Comment: 'italic #888888',
            Token.Comment.Hashbang: '#287088',
            Token.Comment.Multiline: '#888888',
            Token.Comment.Preproc: 'noitalic #289870',
            Token.Comment.PreprocFile: '',
            Token.Comment.Single: '',
            Token.Comment.Special: '',
            Token.Error: 'bg:#a848a8',
            Token.Escape: '',
            Token.Generic: '',
            Token.Generic.Deleted: '#c02828',
            Token.Generic.Emph: 'italic',
            Token.Generic.Error: '#c02828',
            Token.Generic.Heading: '#666666',
            Token.Generic.Inserted: '#388038',
            Token.Generic.Output: '#666666',
            Token.Generic.Prompt: '#444444',
            Token.Generic.Strong: 'bold',
            Token.Generic.Subheading: '#444444',
            Token.Generic.Traceback: '#2838b0',
            Token.Keyword: '#2838b0 bold',
            Token.Keyword.Constant: 'italic #444444',
            Token.Keyword.Declaration: 'italic',
            Token.Keyword.Pseudo: '',
            Token.Keyword.Reserved: '',
            Token.Keyword.Type: 'italic',
            Token.Literal: '',
            Token.Literal.Date: '',
            Token.Literal.Number: '#444444',
            Token.Literal.Number.Bin: '',
            Token.Literal.Number.Float: '',
            Token.Literal.Number.Hex: '',
            Token.Literal.Number.Integer: '',
            Token.Literal.Number.Integer.Long: '',
            Token.Literal.Number.Oct: '',
            Token.Literal.String: '#b83838',
            Token.Literal.String.Backtick: '',
            Token.Literal.String.Char: '#a848a8',
            Token.Literal.String.Doc: 'italic #b85820',
            Token.Literal.String.Double: '',
            Token.Literal.String.Escape: '#709030',
            Token.Literal.String.Heredoc: '',
            Token.Literal.String.Interpol: 'underline',
            Token.Literal.String.Other: '#a848a8',
            Token.Literal.String.Regex: '#a848a8',
            Token.Literal.String.Single: '',
            Token.Literal.String.Symbol: '',
            Token.Name: '',
            Token.Name.Attribute: '#388038',
            Token.Name.Builtin: '#388038',
            Token.Name.Builtin.Pseudo: 'italic',
            Token.Name.Class: '#287088',
            Token.Name.Constant: '#b85820',
            Token.Name.Decorator: '#287088',
            Token.Name.Entity: '#709030',
            Token.Name.Exception: '#908828',
            Token.Name.Function: '#785840',
            Token.Name.Label: '#289870',
            Token.Name.Namespace: '#289870',
            Token.Name.Other: '',
            Token.Name.Property: '',
            Token.Name.Tag: '#2838b0',
            Token.Name.Variable: '#b04040',
            Token.Name.Variable.Class: '',
            Token.Name.Variable.Global: '#908828',
            Token.Name.Variable.Instance: '',
            Token.Operator: '#666666',
            Token.Operator.Word: '#a848a8',
            Token.Other: '',
            Token.Punctuation: '#888888',
            Token.Text: '',
            Token.Text.Whitespace: '#a89028'}

# ryan_style= \
#     {
#         # A rich, colored scheme I made (based on monokai)
#         Comment:"#00ff00",
#         Keyword:'#44ff44',
#         Number:'#378cba',
#         Operator:'',
#         String:'#26b534',
#         Token.Literal.String.Escape :"  #ae81ff",
#         #
#         Name:'',
#         Name.Decorator:'#ff4444',
#         Name.Class:'#ff4444',
#         Name.Function:'#ff4444',
#         Name.Builtin:'#ff4444',
#         #
#         Name.Attribute:'',
#         Name.Constant:'',
#         Name.Entity:'',
#         Name.Exception:'',
#         Name.Label:'',
#         Name.Namespace:'#dcff2d',
#         Name.Tag:'',
#         Name.Variable:'',
#     }


def generate_style(python_style, ui_style):
    """
    Generate Pygments Style class from two dictionaries
    containing style rules.
    """
    assert isinstance(python_style, dict)
    assert isinstance(ui_style, dict)

    styles = {}
    styles.update(DEFAULT_STYLE_EXTENSIONS)
    styles.update(python_style)
    styles.update(ui_style)

    return style_from_dict(styles)


# Code style for Windows consoles. They support only 16 colors,
# so we choose a combination that displays nicely.
win32_code_style = {
    Comment:                   "#00ff00",
    Keyword:                   '#44ff44',
    Number:                    '',
    Operator:                  '',
    String:                    '#ff44ff',

    Name:                      '',
    Name.Decorator:            '#ff4444',
    Name.Class:                '#ff4444',
    Name.Function:             '#ff4444',
    Name.Builtin:              '#ff4444',

    Name.Attribute:            '',
    Name.Constant:             '',
    Name.Entity:               '',
    Name.Exception:            '',
    Name.Label:                '',
    Name.Namespace:            '',
    Name.Tag:                  '',
    Name.Variable:             '',
}
default_ui_style = {
    Token.LineNumber:'#aa6666 bg:#002222',
    # Classic prompt.
    Token.Prompt:                                 'bold',
    Token.Prompt.Dots:                            'noinherit',

    # (IPython <5.0) Prompt: "In [1]:"
    Token.In:                                     'bold #008800',
    Token.In.Number:                              '',

    # Return value.
    Token.Out:                                    '#ff0000',
    Token.Out.Number:                             '#ff0000',

    # Separator between windows. (Used above docstring.)
    Token.Separator:                              '#bbbbbb',

    # Search toolbar.
    Token.Toolbar.Search:                         '#22aaaa noinherit',
    Token.Toolbar.Search.Text:                    'noinherit',

    # System toolbar
    Token.Toolbar.System:                         '#22aaaa noinherit',

    # "arg" toolbar.
    Token.Toolbar.Arg:                            '#22aaaa noinherit',
    Token.Toolbar.Arg.Text:                       'noinherit',

    # Signature toolbar.
    Token.Toolbar.Signature:                      'bg:#44bbbb #000000',
    Token.Toolbar.Signature.CurrentName:          'bg:#008888 #ffffff bold',
    Token.Toolbar.Signature.Operator:             '#000000 bold',

    Token.Docstring:                              '#888888',

    # Validation toolbar.
    Token.Toolbar.Validation:                     'bg:#440000 #aaaaaa',

    # Status toolbar.
    Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',
    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#222222 #22aa22',
    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#222222 #aa2222',
    Token.Toolbar.Status.Title:                   'underline',
    Token.Toolbar.Status.InputMode:               'bg:#222222 #ffffaa',
    Token.Toolbar.Status.Key:                     'bg:#000000 #888888',
    Token.Toolbar.Status.PasteModeOn:             'bg:#aa4444 #ffffff',
    Token.Toolbar.Status.PseudoTerminalCurrentVariable:
        'bg:#662266 #aaaaaa',# RYAN BURGERT STUFF
    Token.Toolbar.Status.PythonVersion:           'bg:#222222 #ffffff bold',

    # When Control-C has been pressed. Grayed.
    Token.Aborted:                                '#888888',

    # The options sidebar.
    Token.Sidebar:                                'bg:#bbbbbb #000000',
    Token.Sidebar.Title:                          'bg:#6688ff #ffffff bold',
    Token.Sidebar.Label:                          'bg:#bbbbbb #222222',
    Token.Sidebar.Status:                         'bg:#dddddd #000011',
    Token.Sidebar.Selected.Label:                 'bg:#222222 #eeeeee',
    Token.Sidebar.Selected.Status:                'bg:#444444 #ffffff bold',

    Token.Sidebar.Separator:                       'bg:#bbbbbb #ffffff underline',
    Token.Sidebar.Key:                            'bg:#bbddbb #000000 bold',
    Token.Sidebar.Key.Description:                'bg:#bbbbbb #000000',
    Token.Sidebar.HelpText:                       'bg:#eeeeff #000011',

    # Styling for the history layout.
    Token.History.Line:                          '',
    Token.History.Line.Selected:                 'bg:#008800  #000000',
    Token.History.Line.Current:                  'bg:#ffffff #000000',
    Token.History.Line.Selected.Current:         'bg:#88ff88 #000000',
    Token.History.ExistingInput:                  '#888888',

    # Help Window.
    Token.Window.Border:                          '#0000bb',
    Token.Window.Title:                           'bg:#bbbbbb #000000',
    Token.Window.TIItleV2:                         'bg:#6688bb #000000 bold',

    # Meta-enter message.
    Token.AcceptMessage:                          'bg:#ffff88 #444444',

    # Exit confirmation.
    Token.ExitConfirmation:                       'bg:#884444 #ffffff',
}

# Some changes to get a bit more contrast on Windows consoles.
# (They only support 16 colors.)
if is_windows() and not is_conemu_ansi():
    default_ui_style.update({
        Token.Sidebar.Title:                          'bg:#00ff00 #ffffff',
        Token.ExitConfirmation:                       'bg:#ff4444 #ffffff',
        Token.Toolbar.Validation:                     'bg:#ff4444 #ffffff',

        Token.Menu.Completions.Completion:            'bg:#ffffff #000000',
        Token.Menu.Completions.Completion.Current:    'bg:#aaaaaa #000000',
    })


blue_ui_style = {}
blue_ui_style.update(default_ui_style)
blue_ui_style.update({
        # Line numbers.
        Token.LineNumber:                             '#aa6666 bg:#222222',

        # Highlighting of search matches in document.
        Token.SearchMatch:                            '#ffffff bg:#4444aa',
        Token.SearchMatch.Current:                    '#ffffff bg:#44aa44',

        # Highlighting of select text in document.
        Token.SelectedText:                           '#ffffff bg:#6666aa',

        # Completer toolbar.
        Token.Toolbar.Completions:                    'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Arrow:              'bg:#44bbbb #000000 bold',
        Token.Toolbar.Completions.Completion:         'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Completion.Current: 'bg:#008888 #ffffff',

        # Completer menu.
        Token.Menu.Completions.Completion:            'bg:#44bbbb #000000',
        Token.Menu.Completions.Completion.Current:    'bg:#008888 #ffffff',
        Token.Menu.Completions.Meta:                  'bg:#449999 #000000',
        Token.Menu.Completions.Meta.Current:          'bg:#00aaaa #000000',
        Token.Menu.Completions.ProgressBar:           'bg:#aaaaaa',
        Token.Menu.Completions.ProgressButton:        'bg:#000000',
})


# HOW I MADE THE INVERSION THEME:
#THIS CODE AUTOMATICALLY MODIFIES COLORS IN THESE THEMES WHICH LETS ME MAKE NEW THEMES
# code="""{Token.LineNumber:'#aa6666 bg:#002222',    Token.Prompt:                                 'bold',Token.Prompt.Dots:                            'noinherit',Token.In:                                     'bold #008800',Token.In.Number:                              '',Token.Out:                                    '#ff0000',Token.Out.Number:                             '#ff0000',Token.Separator:                              '#bbbbbb',Token.Toolbar.Search:                         '#22aaaa noinherit',Token.Toolbar.Search.Text:                    'noinherit',Token.Toolbar.System:                         '#22aaaa noinherit',Token.Toolbar.Arg:                            '#22aaaa noinherit',Token.Toolbar.Arg.Text:                       'noinherit',Token.Toolbar.Signature:                      'bg:#44bbbb #000000',Token.Toolbar.Signature.CurrentName:          'bg:#008888 #ffffff bold',Token.Toolbar.Signature.Operator:             '#000000 bold',Token.Docstring:                              '#888888',Token.Toolbar.Validation:                     'bg:#440000 #aaaaaa',Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',Token.Toolbar.Status.BatteryPluggedIn:        'bg:#222222 #22aa22',Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#222222 #aa2222',Token.Toolbar.Status.Title:                   'underline',Token.Toolbar.Status.InputMode:               'bg:#222222 #ffffaa',Token.Toolbar.Status.Key:                     'bg:#000000 #888888',Token.Toolbar.Status.PasteModeOn:             'bg:#aa4444 #ffffff',Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#662266 #aaaaaa',Token.Toolbar.Status.PythonVersion:           'bg:#222222 #ffffff bold',Token.Aborted:                                '#888888',Token.Sidebar:                                'bg:#bbbbbb #000000',Token.Sidebar.Title:                          'bg:#6688ff #ffffff bold',Token.Sidebar.Label:                          'bg:#bbbbbb #222222',Token.Sidebar.Status:                         'bg:#dddddd #000011',Token.Sidebar.Selected.Label:                 'bg:#222222 #eeeeee',Token.Sidebar.Selected.Status:                'bg:#444444 #ffffff bold',Token.Sidebar.Separator:                       'bg:#bbbbbb #ffffff underline',Token.Sidebar.Key:                            'bg:#bbddbb #000000 bold',Token.Sidebar.Key.Description:                'bg:#bbbbbb #000000',Token.Sidebar.HelpText:                       'bg:#eeeeff #000011',Token.History.Line:                          '',Token.History.Line.Selected:                 'bg:#008800  #000000',Token.History.Line.Current:                  'bg:#ffffff #000000',Token.History.Line.Selected.Current:         'bg:#88ff88 #000000',Token.History.ExistingInput:                  '#888888',Token.Window.Border:                          '#0000bb',Token.Window.Title:                           'bg:#bbbbbb #000000',Token.Window.TIItleV2:                         'bg:#6688bb #000000 bold',Token.AcceptMessage:                          'bg:#ffff88 #444444',Token.ExitConfirmation:                       'bg:#884444 #ffffff',}"""
# def changecolors(colors):
#     return [np.clip((np.roll([x for x in c],1)*2+np.asarray([0,128,255]))//1.5-100,0,255).astype(int) for c in colors]
# def codewithcolors(colors,code=code):
#     x=keys_and_values_to_dict(tocols(allcols(code)),tocols(colors))
#     print(x)
#     return search_replace_simul(code,x)
# def tocols(cols):
#     return [''.join([hex(x)[2:].rjust(2,'0') for x in y]) for y in cols]
# def allcols(code):
#     import re
#     cols=re.findall('#'+r'[\dA-Fa-f]'*6,code)#Colors like 55aaff or 12abfg
#     cols=[x[1:] for x in cols]
#     cols=set(cols)
#     return [[eval('0x'+''.join(x)) for x in split_into_sublists(w,2)] for w in cols]
# colors=allcols(code)
# ans=codewithcolors(changecolors(colors),code)

inverted_3 = {}
inverted_3.update(default_ui_style)

inverted_3 = {}
inverted_3.update(default_ui_style)
inverted_3.update({
    # Status toolbar.
    Token.Toolbar.Status:                         'bg:#dddddd #555555',
    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#dddddd #dd55dd',
    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#dddddd #55dddd',
    Token.Toolbar.Status.Title:                   'underline',
    Token.Toolbar.Status.InputMode:               'bg:#dddddd #000055',
    Token.Toolbar.Status.Key:                     'bg:#ffffff #777777',
    Token.Toolbar.Status.PasteModeOn:             'bg:#55bbbb #000000',
    Token.Toolbar.Status.PseudoTerminalCurrentVariable:
        'bg:#99dd99 #555555',# RYAN BURGERT STUFF
    Token.Toolbar.Status.PythonVersion:           'bg:#dddddd #000000 bold',

    # When Control-C has been pressed. Grayed.
    Token.Aborted:                                '#777777',

    # The options sidebar.
    Token.Sidebar:                                'bg:#444444 #ffffff',
    Token.Sidebar.Title:                          'bg:#997700 #000000 bold',
    Token.Sidebar.Label:                          'bg:#444444 #dddddd',
    Token.Sidebar.Status:                         'bg:#222222 #ffffee',
    Token.Sidebar.Selected.Label:                 'bg:#dddddd #111111',
    Token.Sidebar.Selected.Status:                'bg:#bbbbbb #000000 bold',

    Token.Sidebar.Separator:                       'bg:#444444 #000000 underline',
    Token.Sidebar.Key:                            'bg:#442244 #ffffff bold',
    Token.Sidebar.Key.Description:                'bg:#444444 #ffffff',
    Token.Sidebar.HelpText:                       'bg:#111100 #ffffee',

    # Styling for the history layout.
    Token.History.Line:                          '',
    Token.History.Line.Selected:                 'bg:#ff77ff  #ffffff',
    Token.History.Line.Current:                  'bg:#000000 #ffffff',
    Token.History.Line.Selected.Current:         'bg:#770077 #ffffff',
    Token.History.ExistingInput:                  '#777777',

    # Help Window.
    Token.Window.Border:                          '#ffff44',
    Token.Window.Title:                           'bg:#444444 #ffffff',
    Token.Window.TIItleV2:                         'bg:#997744 #ffffff bold',

    # Meta-enter message.
    Token.AcceptMessage:                          'bg:#000077 #bbbbbb',

    # Exit confirmation.
    Token.ExitConfirmation:                       'bg:#77bbbb #000000',
})

inverted_3.update({
        # Line numbers.
        Token.LineNumber:                             '#aa6666 bg:#222222',

        # Highlighting of search matches in document.
        Token.SearchMatch:                            '#ffffff bg:#4444aa',
        Token.SearchMatch.Current:                    '#ffffff bg:#44aa44',

        # Highlighting of select text in document.
        Token.SelectedText:                           '#ffffff bg:#6666aa',

        # Completer toolbar.
        Token.Toolbar.Completions:                    'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Arrow:              'bg:#44bbbb #000000 bold',
        Token.Toolbar.Completions.Completion:         'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Completion.Current: 'bg:#008888 #ffffff',

        # Completer menu.
        Token.Menu.Completions.Completion:            'bg:#44bbbb #000000',
        Token.Menu.Completions.Completion.Current:    'bg:#008888 #ffffff',
        Token.Menu.Completions.Meta:                  'bg:#449999 #000000',
        Token.Menu.Completions.Meta.Current:          'bg:#00aaaa #000000',
        Token.Menu.Completions.ProgressBar:           'bg:#aaaaaa',
        Token.Menu.Completions.ProgressButton:        'bg:#000000',
})






color_1={    Token.LineNumber:'#d47623 bg:#397300',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #7dfb00',    Token.In.Number:                              '',    Token.Out:                                    '#ff0039',    Token.Out.Number:                             '#ff0039',    Token.Separator:                              '#ffdf94',    Token.Toolbar.Search:                         '#2eff1e noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#2eff1e noinherit',    Token.Toolbar.Arg:                            '#2eff1e noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#5cff4c #234600',    Token.Toolbar.Signature.CurrentName:          'bg:#2cfb00 #fff7f0 bold',    Token.Toolbar.Signature.Operator:             '#234600 bold',    Token.Docstring:                              '#fbfb51',    Token.Toolbar.Validation:                     'bg:#4c2000 #ffe97e',    Token.Toolbar.Status:                         'bg:#577300 #ffe97e',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#577300 #9dff00',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#577300 #d40900',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#577300 #ffbe7e',    Token.Toolbar.Status.Key:                     'bg:#234600 #fbfb51',    Token.Toolbar.Status.PasteModeOn:             'bg:#d43500 #fff7f0',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#794824 #ffe97e',    Token.Toolbar.Status.PythonVersion:           'bg:#577300 #fff7f0 bold',    Token.Aborted:                                '#fbfb51',    Token.Sidebar:                                'bg:#ffdf94 #234600',    Token.Sidebar.Title:                          'bg:#79fbaf #fff7f0 bold',    Token.Sidebar.Label:                          'bg:#ffdf94 #577300',    Token.Sidebar.Status:                         'bg:#ffe0c2 #234600',    Token.Sidebar.Selected.Label:                 'bg:#577300 #ffecd9',    Token.Sidebar.Selected.Status:                'bg:#9ba000 #fff7f0 bold',    Token.Sidebar.Separator:                       'bg:#ffdf94 #fff7f0 underline',    Token.Sidebar.Key:                            'bg:#ffdf94 #234600 bold',    Token.Sidebar.Key.Description:                'bg:#ffdf94 #234600',    Token.Sidebar.HelpText:                       'bg:#fff7f0 #234600',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#7dfb00  #234600',    Token.History.Line.Current:                  'bg:#fff7f0 #234600',    Token.History.Line.Selected.Current:         'bg:#fdff51 #234600',    Token.History.ExistingInput:                  '#fbfb51',    Token.Window.Border:                          '#009095',    Token.Window.Title:                           'bg:#ffdf94 #234600',    Token.Window.TIItleV2:                         'bg:#9dfb79 #234600 bold',    Token.AcceptMessage:                          'bg:#ffa851 #9ba000',    Token.ExitConfirmation:                       'bg:#a64c00 #fff7f0',    Token.LineNumber:                             '#d47623 bg:#577300',        Token.SearchMatch:                            '#fff7f0 bg:#4ca053',        Token.SearchMatch.Current:                    '#fff7f0 bg:#cbff00',        Token.SelectedText:                           '#fff7f0 bg:#9ece78',        Token.Toolbar.Completions:                    'bg:#5cff4c #234600',        Token.Toolbar.Completions.Arrow:              'bg:#5cff4c #234600 bold',        Token.Toolbar.Completions.Completion:         'bg:#5cff4c #234600',        Token.Toolbar.Completions.Completion.Current: 'bg:#2cfb00 #fff7f0',        Token.Menu.Completions.Completion:            'bg:#5cff4c #234600',        Token.Menu.Completions.Completion.Current:    'bg:#2cfb00 #fff7f0',        Token.Menu.Completions.Meta:                  'bg:#89ff4c #234600',        Token.Menu.Completions.Meta.Current:          'bg:#01ff00 #234600',        Token.Menu.Completions.ProgressBar:           'bg:#ffe97e',        Token.Menu.Completions.ProgressButton:        'bg:#234600',}
color_2={    Token.LineNumber:'#1a1ea2 bg:#410040',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #c900c8',    Token.In.Number:                              '',    Token.Out:                                    '#0094cd',    Token.Out.Number:                             '#0094cd',    Token.Separator:                              '#8876cd',    Token.Toolbar.Search:                         '#cd187f noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#cd187f noinherit',    Token.Toolbar.Arg:                            '#cd187f noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#cd3d91 #140014',    Token.Toolbar.Signature.CurrentName:          'bg:#c90087 #c0c1cd bold',    Token.Toolbar.Signature.Operator:             '#140014 bold',    Token.Docstring:                              '#8440c9',    Token.Toolbar.Validation:                     'bg:#00021a #8765cd',    Token.Toolbar.Status:                         'bg:#300041 #8765cd',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#300041 #b500cd',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#300041 #004aa2',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#300041 #6565cd',    Token.Toolbar.Status.Key:                     'bg:#140014 #8440c9',    Token.Toolbar.Status.PasteModeOn:             'bg:#0028a2 #c0c1cd',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#151847 #8765cd',    Token.Toolbar.Status.PythonVersion:           'bg:#300041 #c0c1cd bold',    Token.Aborted:                                '#8440c9',    Token.Sidebar:                                'bg:#8876cd #140014',    Token.Sidebar.Title:                          'bg:#c96069 #c0c1cd bold',    Token.Sidebar.Label:                          'bg:#8876cd #300041',    Token.Sidebar.Status:                         'bg:#9b9ccd #140014',    Token.Sidebar.Selected.Label:                 'bg:#300041 #aeaecd',    Token.Sidebar.Selected.Status:                'bg:#3a006e #c0c1cd bold',    Token.Sidebar.Separator:                       'bg:#8876cd #c0c1cd underline',    Token.Sidebar.Key:                            'bg:#8876cd #140014 bold',    Token.Sidebar.Key.Description:                'bg:#8876cd #140014',    Token.Sidebar.HelpText:                       'bg:#c0c1cd #140014',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#c900c8  #140014',    Token.History.Line.Current:                  'bg:#c0c1cd #140014',    Token.History.Line.Selected.Current:         'bg:#8841cd #140014',    Token.History.ExistingInput:                  '#8440c9',    Token.Window.Border:                          '#633400',    Token.Window.Title:                           'bg:#8876cd #140014',    Token.Window.TIItleV2:                         'bg:#c960b1 #140014 bold',    Token.AcceptMessage:                          'bg:#4141cd #3a006e',    Token.ExitConfirmation:                       'bg:#000474 #c0c1cd',    Token.LineNumber:                             '#1a1ea2 bg:#300041',        Token.SearchMatch:                            '#c0c1cd bg:#6e344c',        Token.SearchMatch.Current:                    '#c0c1cd bg:#9000cd',        Token.SelectedText:                           '#c0c1cd bg:#9c5a98',        Token.Toolbar.Completions:                    'bg:#cd3d91 #140014',        Token.Toolbar.Completions.Arrow:              'bg:#cd3d91 #140014 bold',        Token.Toolbar.Completions.Completion:         'bg:#cd3d91 #140014',        Token.Toolbar.Completions.Completion.Current: 'bg:#c90087 #c0c1cd',        Token.Menu.Completions.Completion:            'bg:#cd3d91 #140014',        Token.Menu.Completions.Completion.Current:    'bg:#c90087 #c0c1cd',        Token.Menu.Completions.Meta:                  'bg:#cd3db6 #140014',        Token.Menu.Completions.Meta.Current:          'bg:#cd0067 #140014',        Token.Menu.Completions.ProgressBar:           'bg:#8765cd',        Token.Menu.Completions.ProgressButton:        'bg:#140014',}
color_3={    Token.LineNumber:'#5ea28b bg:#202941',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #6482c9',    Token.In.Number:                              '',    Token.Out:                                    '#68cd66',    Token.Out.Number:                             '#68cd66',    Token.Separator:                              '#a1cdc8',    Token.Toolbar.Search:                         '#7e72cd noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#7e72cd noinherit',    Token.Toolbar.Arg:                            '#7e72cd noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#8d85cd #0a0c14',    Token.Toolbar.Signature.CurrentName:          'bg:#6764c9 #c6cdca bold',    Token.Toolbar.Signature.Operator:             '#0a0c14 bold',    Token.Docstring:                              '#84bbc9',    Token.Toolbar.Validation:                     'bg:#0d1a15 #99cbcd',    Token.Toolbar.Status:                         'bg:#203241 #99cbcd',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#203241 #6691cd',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#203241 #51a264',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#203241 #99cdbd',    Token.Toolbar.Status.Key:                     'bg:#0a0c14 #84bbc9',    Token.Toolbar.Status.PasteModeOn:             'bg:#51a275 #c6cdca',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#2e473e #99cbcd',    Token.Toolbar.Status.PythonVersion:           'bg:#203241 #c6cdca bold',    Token.Aborted:                                '#84bbc9',    Token.Sidebar:                                'bg:#a1cdc8 #0a0c14',    Token.Sidebar.Title:                          'bg:#b494c9 #c6cdca bold',    Token.Sidebar.Label:                          'bg:#a1cdc8 #203241',    Token.Sidebar.Status:                         'bg:#b4cdc5 #0a0c14',    Token.Sidebar.Selected.Label:                 'bg:#203241 #bdcdc8',    Token.Sidebar.Selected.Status:                'bg:#37616e #c6cdca bold',    Token.Sidebar.Separator:                       'bg:#a1cdc8 #c6cdca underline',    Token.Sidebar.Key:                            'bg:#a1cdc8 #0a0c14 bold',    Token.Sidebar.Key.Description:                'bg:#a1cdc8 #0a0c14',    Token.Sidebar.HelpText:                       'bg:#c6cdca #0a0c14',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#6482c9  #0a0c14',    Token.History.Line.Current:                  'bg:#c6cdca #0a0c14',    Token.History.Line.Selected.Current:         'bg:#86becd #0a0c14',    Token.History.ExistingInput:                  '#84bbc9',    Token.Window.Border:                          '#633157',    Token.Window.Title:                           'bg:#a1cdc8 #0a0c14',    Token.Window.TIItleV2:                         'bg:#9498c9 #0a0c14 bold',    Token.AcceptMessage:                          'bg:#86cdb8 #37616e',    Token.ExitConfirmation:                       'bg:#3a7460 #c6cdca',    Token.LineNumber:                             '#5ea28b bg:#203241',        Token.SearchMatch:                            '#c6cdca bg:#59516e',        Token.SearchMatch.Current:                    '#c6cdca bg:#66a3cd',        Token.SelectedText:                           '#c6cdca bg:#7b829c',        Token.Toolbar.Completions:                    'bg:#8d85cd #0a0c14',        Token.Toolbar.Completions.Arrow:              'bg:#8d85cd #0a0c14 bold',        Token.Toolbar.Completions.Completion:         'bg:#8d85cd #0a0c14',        Token.Toolbar.Completions.Completion.Current: 'bg:#6764c9 #c6cdca',        Token.Menu.Completions.Completion:            'bg:#8d85cd #0a0c14',        Token.Menu.Completions.Completion.Current:    'bg:#6764c9 #c6cdca',        Token.Menu.Completions.Meta:                  'bg:#858fcd #0a0c14',        Token.Menu.Completions.Meta.Current:          'bg:#7a66cd #0a0c14',        Token.Menu.Completions.ProgressBar:           'bg:#99cbcd',        Token.Menu.Completions.ProgressButton:        'bg:#0a0c14',}

pupper={    Token.LineNumber:'#23d452 bg:#005073',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #00affb',    Token.In.Number:                              '',    Token.Out:                                    '#6cff00',    Token.Out.Number:                             '#6cff00',    Token.Separator:                              '#94ffc9',    Token.Toolbar.Search:                         '#1e5bff noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#1e5bff noinherit',    Token.Toolbar.Arg:                            '#1e5bff noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#4c80ff #003046',    Token.Toolbar.Signature.CurrentName:          'bg:#005efb #f0fff4 bold',    Token.Toolbar.Signature.Operator:             '#003046 bold',    Token.Docstring:                              '#51fbd8',    Token.Toolbar.Validation:                     'bg:#004c10 #7effcf',    Token.Toolbar.Status:                         'bg:#006e73 #7effcf',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#006e73 #00d0ff',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#006e73 #21d400',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#006e73 #7effa4',    Token.Toolbar.Status.Key:                     'bg:#003046 #51fbd8',    Token.Toolbar.Status.PasteModeOn:             'bg:#00d40b #f0fff4',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#247937 #7effcf',    Token.Toolbar.Status.PythonVersion:           'bg:#006e73 #f0fff4 bold',    Token.Aborted:                                '#51fbd8',    Token.Sidebar:                                'bg:#94ffc9 #003046',    Token.Sidebar.Title:                          'bg:#9479fb #f0fff4 bold',    Token.Sidebar.Label:                          'bg:#94ffc9 #006e73',    Token.Sidebar.Status:                         'bg:#c2ffd4 #003046',    Token.Sidebar.Selected.Label:                 'bg:#006e73 #d9ffe4',    Token.Sidebar.Selected.Status:                'bg:#00a084 #f0fff4 bold',    Token.Sidebar.Separator:                       'bg:#94ffc9 #f0fff4 underline',    Token.Sidebar.Key:                            'bg:#94ffc9 #003046 bold',    Token.Sidebar.Key.Description:                'bg:#94ffc9 #003046',    Token.Sidebar.HelpText:                       'bg:#f0fff4 #003046',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#00affb  #003046',    Token.History.Line.Current:                  'bg:#f0fff4 #003046',    Token.History.Line.Selected.Current:         'bg:#51ffde #003046',    Token.History.ExistingInput:                  '#51fbd8',    Token.Window.Border:                          '#7b0095',    Token.Window.Title:                           'bg:#94ffc9 #003046',    Token.Window.TIItleV2:                         'bg:#79b8fb #003046 bold',    Token.AcceptMessage:                          'bg:#51ff85 #00a084',    Token.ExitConfirmation:                       'bg:#00a62b #f0fff4',    Token.LineNumber:                             '#23d452 bg:#006e73',        Token.SearchMatch:                            '#f0fff4 bg:#4c54a0',        Token.SearchMatch.Current:                    '#f0fff4 bg:#00feff',        Token.SelectedText:                           '#f0fff4 bg:#78afce',        Token.Toolbar.Completions:                    'bg:#4c80ff #003046',        Token.Toolbar.Completions.Arrow:              'bg:#4c80ff #003046 bold',        Token.Toolbar.Completions.Completion:         'bg:#4c80ff #003046',        Token.Toolbar.Completions.Completion.Current: 'bg:#005efb #f0fff4',        Token.Menu.Completions.Completion:            'bg:#4c80ff #003046',        Token.Menu.Completions.Completion.Current:    'bg:#005efb #f0fff4',        Token.Menu.Completions.Meta:                  'bg:#4cadff #003046',        Token.Menu.Completions.Meta.Current:          'bg:#0034ff #003046',        Token.Menu.Completions.ProgressBar:           'bg:#7effcf',        Token.Menu.Completions.ProgressButton:        'bg:#003046',}
clara={    Token.LineNumber:'#7bced4 bg:#3f3973',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #8a7dfb',    Token.In.Number:                              '',    Token.Out:                                    '#7fffaf',    Token.Out.Number:                             '#7fffaf',    Token.Separator:                              '#c9efff',    Token.Toolbar.Search:                         '#ca8eff noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#ca8eff noinherit',    Token.Toolbar.Arg:                            '#ca8eff noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#d3a5ff #262346',    Token.Toolbar.Signature.CurrentName:          'bg:#b27dfb #f7feff bold',    Token.Toolbar.Signature.Operator:             '#262346 bold',    Token.Docstring:                              '#a6c8fb',    Token.Toolbar.Validation:                     'bg:#264b4c #bee3ff',    Token.Toolbar.Status:                         'bg:#394273 #bee3ff',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#394273 #7f81ff',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#394273 #6ad4ae',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#394273 #bef8ff',    Token.Toolbar.Status.Key:                     'bg:#262346 #a6c8fb',    Token.Toolbar.Status.PasteModeOn:             'bg:#6ad4c4 #f7feff',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#4e7879 #bee3ff',    Token.Toolbar.Status.PythonVersion:           'bg:#394273 #f7feff bold',    Token.Aborted:                                '#a6c8fb',    Token.Sidebar:                                'bg:#c9efff #262346',    Token.Sidebar.Title:                          'bg:#fbbafa #f7feff bold',    Token.Sidebar.Label:                          'bg:#c9efff #394273',    Token.Sidebar.Status:                         'bg:#e0fcff #262346',    Token.Sidebar.Selected.Label:                 'bg:#394273 #ecfdff',    Token.Sidebar.Selected.Status:                'bg:#506da0 #f7feff bold',    Token.Sidebar.Separator:                       'bg:#c9efff #f7feff underline',    Token.Sidebar.Key:                            'bg:#c9efff #262346 bold',    Token.Sidebar.Key.Description:                'bg:#c9efff #262346',    Token.Sidebar.HelpText:                       'bg:#f7feff #262346',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#8a7dfb  #262346',    Token.History.Line.Current:                  'bg:#f7feff #262346',    Token.History.Line.Selected.Current:         'bg:#a8c9ff #262346',    Token.History.ExistingInput:                  '#a6c8fb',    Token.Window.Border:                          '#954a66',    Token.Window.Title:                           'bg:#c9efff #262346',    Token.Window.TIItleV2:                         'bg:#cebafb #262346 bold',    Token.AcceptMessage:                          'bg:#a8f6ff #506da0',    Token.ExitConfirmation:                       'bg:#53a1a6 #f7feff',    Token.LineNumber:                             '#7bced4 bg:#394273',        Token.SearchMatch:                            '#f7feff bg:#9376a0',        Token.SearchMatch.Current:                    '#f7feff bg:#7f98ff',        Token.SelectedText:                           '#f7feff bg:#a9a3ce',        Token.Toolbar.Completions:                    'bg:#d3a5ff #262346',        Token.Toolbar.Completions.Arrow:              'bg:#d3a5ff #262346 bold',        Token.Toolbar.Completions.Completion:         'bg:#d3a5ff #262346',        Token.Toolbar.Completions.Completion.Current: 'bg:#b27dfb #f7feff',        Token.Menu.Completions.Completion:            'bg:#d3a5ff #262346',        Token.Menu.Completions.Completion.Current:    'bg:#b27dfb #f7feff',        Token.Menu.Completions.Meta:                  'bg:#bca5ff #262346',        Token.Menu.Completions.Meta.Current:          'bg:#cb7fff #262346',        Token.Menu.Completions.ProgressBar:           'bg:#bee3ff',        Token.Menu.Completions.ProgressButton:        'bg:#262346',}
emma={    Token.LineNumber:'#7b86d4 bg:#6d3973',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #ee7dfb',    Token.In.Number:                              '',    Token.Out:                                    '#7fe8ff',    Token.Out.Number:                             '#7fe8ff',    Token.Separator:                              '#cec9ff',    Token.Toolbar.Search:                         '#ff8ed9 noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#ff8ed9 noinherit',    Token.Toolbar.Arg:                            '#ff8ed9 noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#ffa4e3 #412346',    Token.Toolbar.Signature.CurrentName:          'bg:#fb7ddf #f7f7ff bold',    Token.Toolbar.Signature.Operator:             '#412346 bold',    Token.Docstring:                              '#c8a6fb',    Token.Toolbar.Validation:                     'bg:#262c4c #cdbeff',    Token.Toolbar.Status:                         'bg:#5e3973 #cdbeff',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#5e3973 #e37fff',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#5e3973 #6aa5d4',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#5e3973 #bec4ff',    Token.Toolbar.Status.Key:                     'bg:#412346 #c8a6fb',    Token.Toolbar.Status.PasteModeOn:             'bg:#6a8fd4 #f7f7ff',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#4e5579 #cdbeff',    Token.Toolbar.Status.PythonVersion:           'bg:#5e3973 #f7f7ff bold',    Token.Aborted:                                '#c8a6fb',    Token.Sidebar:                                'bg:#cec9ff #412346',    Token.Sidebar.Title:                          'bg:#fbbac6 #f7f7ff bold',    Token.Sidebar.Label:                          'bg:#cec9ff #5e3973',    Token.Sidebar.Status:                         'bg:#e0e3ff #412346',    Token.Sidebar.Selected.Label:                 'bg:#5e3973 #ecedff',    Token.Sidebar.Selected.Status:                'bg:#7350a0 #f7f7ff bold',    Token.Sidebar.Separator:                       'bg:#cec9ff #f7f7ff underline',    Token.Sidebar.Key:                            'bg:#cec9ff #412346 bold',    Token.Sidebar.Key.Description:                'bg:#cec9ff #412346',    Token.Sidebar.HelpText:                       'bg:#f7f7ff #412346',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#ee7dfb  #412346',    Token.History.Line.Current:                  'bg:#f7f7ff #412346',    Token.History.Line.Selected.Current:         'bg:#cca8ff #412346',    Token.History.ExistingInput:                  '#c8a6fb',    Token.Window.Border:                          '#956a49',    Token.Window.Title:                           'bg:#cec9ff #412346',    Token.Window.TIItleV2:                         'bg:#fbbaf4 #412346 bold',    Token.AcceptMessage:                          'bg:#a8b0ff #7350a0',    Token.ExitConfirmation:                       'bg:#535ea6 #f7f7ff',    Token.LineNumber:                             '#7b86d4 bg:#5e3973',        Token.SearchMatch:                            '#f7f7ff bg:#a0768b',        Token.SearchMatch.Current:                    '#f7f7ff bg:#cc7fff',        Token.SelectedText:                           '#f7f7ff bg:#cba3ce',        Token.Toolbar.Completions:                    'bg:#ffa4e3 #412346',        Token.Toolbar.Completions.Arrow:              'bg:#ffa4e3 #412346 bold',        Token.Toolbar.Completions.Completion:         'bg:#ffa4e3 #412346',        Token.Toolbar.Completions.Completion.Current: 'bg:#fb7ddf #f7f7ff',        Token.Menu.Completions.Completion:            'bg:#ffa4e3 #412346',        Token.Menu.Completions.Completion.Current:    'bg:#fb7ddf #f7f7ff',        Token.Menu.Completions.Meta:                  'bg:#ffa4fa #412346',        Token.Menu.Completions.Meta.Current:          'bg:#ff7fcc #412346',        Token.Menu.Completions.ProgressBar:           'bg:#cdbeff',        Token.Menu.Completions.ProgressButton:        'bg:#412346',}


base={    Token.LineNumber:'#aa6666 bg:#002222',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #008800',    Token.In.Number:                              '',    Token.Out:                                    '#ff0000',    Token.Out.Number:                             '#ff0000',    Token.Separator:                              '#bbbbbb',    Token.Toolbar.Search:                         '#22aaaa noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#22aaaa noinherit',    Token.Toolbar.Arg:                            '#22aaaa noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#44bbbb #000000',    Token.Toolbar.Signature.CurrentName:          'bg:#008888 #ffffff bold',    Token.Toolbar.Signature.Operator:             '#000000 bold',    Token.Docstring:                              '#888888',    Token.Toolbar.Validation:                     'bg:#440000 #aaaaaa',    Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#222222 #22aa22',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#222222 #aa2222',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#222222 #ffffaa',    Token.Toolbar.Status.Key:                     'bg:#000000 #888888',    Token.Toolbar.Status.PasteModeOn:             'bg:#aa4444 #ffffff',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#662266 #aaaaaa',    Token.Toolbar.Status.PythonVersion:           'bg:#222222 #ffffff bold',    Token.Aborted:                                '#888888',    Token.Sidebar:                                'bg:#bbbbbb #000000',    Token.Sidebar.Title:                          'bg:#6688ff #ffffff bold',    Token.Sidebar.Label:                          'bg:#bbbbbb #222222',    Token.Sidebar.Status:                         'bg:#dddddd #000011',    Token.Sidebar.Selected.Label:                 'bg:#222222 #eeeeee',    Token.Sidebar.Selected.Status:                'bg:#444444 #ffffff bold',    Token.Sidebar.Separator:                       'bg:#bbbbbb #ffffff underline',    Token.Sidebar.Key:                            'bg:#bbddbb #000000 bold',    Token.Sidebar.Key.Description:                'bg:#bbbbbb #000000',    Token.Sidebar.HelpText:                       'bg:#eeeeff #000011',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#008800  #000000',    Token.History.Line.Current:                  'bg:#ffffff #000000',    Token.History.Line.Selected.Current:         'bg:#88ff88 #000000',    Token.History.ExistingInput:                  '#888888',    Token.Window.Border:                          '#0000bb',    Token.Window.Title:                           'bg:#bbbbbb #000000',    Token.Window.TIItleV2:                         'bg:#6688bb #000000 bold',    Token.AcceptMessage:                          'bg:#ffff88 #444444',    Token.ExitConfirmation:                       'bg:#884444 #ffffff',    Token.LineNumber:                             '#aa6666 bg:#222222',        Token.SearchMatch:                            '#ffffff bg:#4444aa',        Token.SearchMatch.Current:                    '#ffffff bg:#44aa44',        Token.SelectedText:                           '#ffffff bg:#6666aa',        Token.Toolbar.Completions:                    'bg:#44bbbb #000000',        Token.Toolbar.Completions.Arrow:              'bg:#44bbbb #000000 bold',        Token.Toolbar.Completions.Completion:         'bg:#44bbbb #000000',        Token.Toolbar.Completions.Completion.Current: 'bg:#008888 #ffffff',        Token.Menu.Completions.Completion:            'bg:#44bbbb #000000',        Token.Menu.Completions.Completion.Current:    'bg:#008888 #ffffff',        Token.Menu.Completions.Meta:                  'bg:#449999 #000000',        Token.Menu.Completions.Meta.Current:          'bg:#00aaaa #000000',        Token.Menu.Completions.ProgressBar:           'bg:#aaaaaa',        Token.Menu.Completions.ProgressButton:        'bg:#000000',}

inverted_1 = {Token.LineNumber:'#aa6666 bg:#002222',    Token.Prompt:                                 'bold',Token.Prompt.Dots:                            'noinherit',Token.In:                                     'bold #008800',Token.In.Number:                              '',Token.Out:                                    '#ff0000',Token.Out.Number:                             '#ff0000',Token.Separator:                              '#bbbbbb',Token.Toolbar.Search:                         '#22aaaa noinherit',Token.Toolbar.Search.Text:                    'noinherit',Token.Toolbar.System:                         '#22aaaa noinherit',Token.Toolbar.Arg:                            '#22aaaa noinherit',Token.Toolbar.Arg.Text:                       'noinherit',Token.Toolbar.Signature:                      'bg:#44bbbb #000000',Token.Toolbar.Signature.CurrentName:          'bg:#008888 #ffffff bold',Token.Toolbar.Signature.Operator:             '#000000 bold',Token.Docstring:                              '#888888',Token.Toolbar.Validation:                     'bg:#440000 #aaaaaa',Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',Token.Toolbar.Status.BatteryPluggedIn:        'bg:#222222 #22aa22',Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#222222 #aa2222',Token.Toolbar.Status.Title:                   'underline',Token.Toolbar.Status.InputMode:               'bg:#222222 #ffffaa',Token.Toolbar.Status.Key:                     'bg:#000000 #888888',Token.Toolbar.Status.PasteModeOn:             'bg:#aa4444 #ffffff',Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#662266 #aaaaaa',Token.Toolbar.Status.PythonVersion:           'bg:#222222 #ffffff bold',Token.Aborted:                                '#888888',Token.Sidebar:                                'bg:#bbbbbb #000000',Token.Sidebar.Title:                          'bg:#6688ff #ffffff bold',Token.Sidebar.Label:                          'bg:#bbbbbb #222222',Token.Sidebar.Status:                         'bg:#dddddd #000011',Token.Sidebar.Selected.Label:                 'bg:#222222 #eeeeee',Token.Sidebar.Selected.Status:                'bg:#444444 #ffffff bold',Token.Sidebar.Separator:                       'bg:#bbbbbb #ffffff underline',Token.Sidebar.Key:                            'bg:#bbddbb #000000 bold',Token.Sidebar.Key.Description:                'bg:#bbbbbb #000000',Token.Sidebar.HelpText:                       'bg:#eeeeff #000011',Token.History.Line:                          '',Token.History.Line.Selected:                 'bg:#008800  #000000',Token.History.Line.Current:                  'bg:#ffffff #000000',Token.History.Line.Selected.Current:         'bg:#88ff88 #000000',Token.History.ExistingInput:                  '#888888',Token.Window.Border:                          '#0000bb',Token.Window.Title:                           'bg:#bbbbbb #000000',Token.Window.TIItleV2:                         'bg:#6688bb #000000 bold',Token.AcceptMessage:                          'bg:#ffff88 #444444',Token.ExitConfirmation:                       'bg:#884444 #ffffff',}
inverted_2 = {Token.LineNumber:'#999955 bg:#ddddff',    Token.Prompt:                                 'bold',Token.Prompt.Dots:                            'noinherit',Token.In:                                     'bold #77ffff',Token.In.Number:                              '',Token.Out:                                    '#ffff00',Token.Out.Number:                             '#ffff00',Token.Separator:                              '#444444',Token.Toolbar.Search:                         '#5555dd noinherit',Token.Toolbar.Search.Text:                    'noinherit',Token.Toolbar.System:                         '#5555dd noinherit',Token.Toolbar.Arg:                            '#5555dd noinherit',Token.Toolbar.Arg.Text:                       'noinherit',Token.Toolbar.Signature:                      'bg:#4444bb #ffffff',Token.Toolbar.Signature.CurrentName:          'bg:#7777ff #000000 bold',Token.Toolbar.Signature.Operator:             '#ffffff bold',Token.Docstring:                              '#777777',Token.Toolbar.Validation:                     'bg:#ffffbb #555555',Token.Toolbar.Status:                         'bg:#dddddd #555555',Token.Toolbar.Status.BatteryPluggedIn:        'bg:#dddddd #55dddd',Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#dddddd #dddd55',Token.Toolbar.Status.Title:                   'underline',Token.Toolbar.Status.InputMode:               'bg:#dddddd #005500',Token.Toolbar.Status.Key:                     'bg:#ffffff #777777',Token.Toolbar.Status.PasteModeOn:             'bg:#bbbb55 #000000',Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#dd9999 #555555',Token.Toolbar.Status.PythonVersion:           'bg:#dddddd #000000 bold',Token.Aborted:                                '#777777',Token.Sidebar:                                'bg:#444444 #ffffff',Token.Sidebar.Title:                          'bg:#770099 #000000 bold',Token.Sidebar.Label:                          'bg:#444444 #dddddd',Token.Sidebar.Status:                         'bg:#222222 #ffeeff',Token.Sidebar.Selected.Label:                 'bg:#dddddd #111111',Token.Sidebar.Selected.Status:                'bg:#bbbbbb #000000 bold',Token.Sidebar.Separator:                       'bg:#444444 #000000 underline',Token.Sidebar.Key:                            'bg:#224444 #ffffff bold',Token.Sidebar.Key.Description:                'bg:#444444 #ffffff',Token.Sidebar.HelpText:                       'bg:#110011 #ffeeff',Token.History.Line:                          '',Token.History.Line.Selected:                 'bg:#77ffff  #ffffff',Token.History.Line.Current:                  'bg:#000000 #ffffff',Token.History.Line.Selected.Current:         'bg:#007777 #ffffff',Token.History.ExistingInput:                  '#777777',Token.Window.Border:                          '#ff44ff',Token.Window.Title:                           'bg:#444444 #ffffff',Token.Window.TIItleV2:                         'bg:#774499 #ffffff bold',Token.AcceptMessage:                          'bg:#007700 #bbbbbb',Token.ExitConfirmation:                       'bg:#bbbb77 #000000',}

cyan = {Token.LineNumber:'#6663bb bg:#93d4e8',    Token.Prompt:                                 'bold',Token.Prompt.Dots:                            'noinherit',Token.In:                                     'bold #aad4a4',Token.In.Number:                              '',Token.Out:                                    '#aa2aff',Token.Out.Number:                             '#aa2aff',Token.Separator:                              '#2d5882',Token.Toolbar.Search:                         '#38be8d noinherit',Token.Toolbar.Search.Text:                    'noinherit',Token.Toolbar.System:                         '#38be8d noinherit',Token.Toolbar.Arg:                            '#38be8d noinherit',Token.Toolbar.Arg.Text:                       'noinherit',Token.Toolbar.Signature:                      'bg:#2da782 #aad4ff',Token.Toolbar.Signature.CurrentName:          'bg:#4fd4a4 #002a55 bold',Token.Toolbar.Signature.Operator:             '#aad4ff bold',Token.Docstring:                              '#4f7aa4',Token.Toolbar.Validation:                     'bg:#aaa7ff #38638d',Token.Toolbar.Status:                         'bg:#93bee8 #38638d',Token.Toolbar.Status.BatteryPluggedIn:        'bg:#93bee8 #93be8d',Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#93bee8 #9363e8',Token.Toolbar.Status.Title:                   'underline',Token.Toolbar.Status.InputMode:               'bg:#93bee8 #382a55',Token.Toolbar.Status.Key:                     'bg:#aad4ff #4f7aa4',Token.Toolbar.Status.PasteModeOn:             'bg:#7c63d1 #002a55',Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#6690e8 #38638d',Token.Toolbar.Status.PythonVersion:           'bg:#93bee8 #002a55 bold',Token.Aborted:                                '#4f7aa4',Token.Sidebar:                                'bg:#2d5882 #aad4ff',Token.Sidebar.Title:                          'bg:#0090a4 #002a55 bold',Token.Sidebar.Label:                          'bg:#2d5882 #93bee8',Token.Sidebar.Status:                         'bg:#16416b #9ed4ff',Token.Sidebar.Selected.Label:                 'bg:#93bee8 #0b3660',Token.Sidebar.Selected.Status:                'bg:#7ca7d1 #002a55 bold',Token.Sidebar.Separator:                       'bg:#2d5882 #002a55 underline',Token.Sidebar.Key:                            'bg:#2d586b #aad4ff bold',Token.Sidebar.Key.Description:                'bg:#2d5882 #aad4ff',Token.Sidebar.HelpText:                       'bg:#003660 #9ed4ff',Token.History.Line:                          '',Token.History.Line.Selected:                 'bg:#aad4a4  #aad4ff',Token.History.Line.Current:                  'bg:#002a55 #aad4ff',Token.History.Line.Selected.Current:         'bg:#4f7a55 #aad4ff',Token.History.ExistingInput:                  '#4f7aa4',Token.Window.Border:                          '#2dd4ff',Token.Window.Title:                           'bg:#2d5882 #aad4ff',Token.Window.TIItleV2:                         'bg:#2d90a4 #aad4ff bold',Token.AcceptMessage:                          'bg:#4f2a55 #7ca7d1',Token.ExitConfirmation:                       'bg:#7c7ad1 #002a55',}
cyan_2={Token.LineNumber:'#51bbb7 bg:#1b3381',    Token.Prompt:                                 'bold',Token.Prompt.Dots:                            'noinherit',Token.In:                                     'bold #0033d2',Token.In.Number:                              '',Token.Out:                                    '#00ff66',Token.Out.Number:                             '#00ff66',Token.Separator:                              '#95c8fb',Token.Toolbar.Search:                         '#884eee noinherit',Token.Toolbar.Search.Text:                    'noinherit',Token.Toolbar.System:                         '#884eee noinherit',Token.Toolbar.Arg:                            '#884eee noinherit',Token.Toolbar.Arg.Text:                       'noinherit',Token.Toolbar.Signature:                      'bg:#9569fb #003366',Token.Toolbar.Signature.CurrentName:          'bg:#6c33d2 #ccffff bold',Token.Toolbar.Signature.Operator:             '#003366 bold',Token.Docstring:                              '#6ca0d2',Token.Toolbar.Validation:                     'bg:#006966 #88bbee',Token.Toolbar.Status:                         'bg:#1b4e81 #88bbee',Token.Toolbar.Status.BatteryPluggedIn:        'bg:#1b4e81 #1b4eee',Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#1b4e81 #1bbb81',Token.Toolbar.Status.Title:                   'underline',Token.Toolbar.Status.InputMode:               'bg:#1b4e81 #88ffff',Token.Toolbar.Status.Key:                     'bg:#003366 #6ca0d2',Token.Toolbar.Status.PasteModeOn:             'bg:#36bb9c #ccffff',Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#518481 #88bbee',Token.Toolbar.Status.PythonVersion:           'bg:#1b4e81 #ccffff bold',Token.Aborted:                                '#6ca0d2',Token.Sidebar:                                'bg:#95c8fb #003366',Token.Sidebar.Title:                          'bg:#cc84d2 #ccffff bold',Token.Sidebar.Label:                          'bg:#95c8fb #1b4e81',Token.Sidebar.Status:                         'bg:#b0e4ff #0d3366',Token.Sidebar.Selected.Label:                 'bg:#1b4e81 #bef1ff',Token.Sidebar.Selected.Status:                'bg:#36699c #ccffff bold',Token.Sidebar.Separator:                       'bg:#95c8fb #ccffff underline',Token.Sidebar.Key:                            'bg:#95c8ff #003366 bold',Token.Sidebar.Key.Description:                'bg:#95c8fb #003366',Token.Sidebar.HelpText:                       'bg:#ccf1ff #0d3366',Token.History.Line:                          '',Token.History.Line.Selected:                 'bg:#0033d2  #003366',Token.History.Line.Current:                  'bg:#ccffff #003366',Token.History.Line.Selected.Current:         'bg:#6ca0ff #003366',Token.History.ExistingInput:                  '#6ca0d2',Token.Window.Border:                          '#953366',Token.Window.Title:                           'bg:#95c8fb #003366',Token.Window.TIItleV2:                         'bg:#9584d2 #003366 bold',Token.AcceptMessage:                          'bg:#6cffff #36699c',Token.ExitConfirmation:                       'bg:#36a09c #ccffff',}
cyan_3={Token.LineNumber:'#24d4ce bg:#000073',    Token.Prompt:                                 'bold',Token.Prompt.Dots:                            'noinherit',Token.In:                                     'bold #0000fb',Token.In.Number:                              '',Token.Out:                                    '#00ff46',Token.Out.Number:                             '#00ff46',Token.Separator:                              '#95eaff',Token.Toolbar.Search:                         '#7e1eff noinherit',Token.Toolbar.Search.Text:                    'noinherit',Token.Toolbar.System:                         '#7e1eff noinherit',Token.Toolbar.Arg:                            '#7e1eff noinherit',Token.Toolbar.Arg.Text:                       'noinherit',Token.Toolbar.Signature:                      'bg:#954cff #000046',Token.Toolbar.Signature.CurrentName:          'bg:#5100fb #f0ffff bold',Token.Toolbar.Signature.Operator:             '#000046 bold',Token.Docstring:                              '#51a6fb',Token.Toolbar.Validation:                     'bg:#004c46 #7ed4ff',Token.Toolbar.Status:                         'bg:#001e73 #7ed4ff',Token.Toolbar.Status.BatteryPluggedIn:        'bg:#001e73 #001eff',Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#001e73 #00d473',Token.Toolbar.Status.Title:                   'underline',Token.Toolbar.Status.InputMode:               'bg:#001e73 #7effff',Token.Toolbar.Status.Key:                     'bg:#000046 #51a6fb',Token.Toolbar.Status.PasteModeOn:             'bg:#00d4a0 #f0ffff',Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#247973 #7ed4ff',Token.Toolbar.Status.PythonVersion:           'bg:#001e73 #f0ffff bold',Token.Aborted:                                '#51a6fb',Token.Sidebar:                                'bg:#95eaff #000046',Token.Sidebar.Title:                          'bg:#f079fb #f0ffff bold',Token.Sidebar.Label:                          'bg:#95eaff #001e73',Token.Sidebar.Status:                         'bg:#c2ffff #000046',Token.Sidebar.Selected.Label:                 'bg:#001e73 #d9ffff',Token.Sidebar.Selected.Status:                'bg:#004ca0 #f0ffff bold',Token.Sidebar.Separator:                       'bg:#95eaff #f0ffff underline',Token.Sidebar.Key:                            'bg:#95eaff #000046 bold',Token.Sidebar.Key.Description:                'bg:#95eaff #000046',Token.Sidebar.HelpText:                       'bg:#f0ffff #000046',Token.History.Line:                          '',Token.History.Line.Selected:                 'bg:#0000fb  #000046',Token.History.Line.Current:                  'bg:#f0ffff #000046',Token.History.Line.Selected.Current:         'bg:#51a6ff #000046',Token.History.ExistingInput:                  '#51a6fb',Token.Window.Border:                          '#950046',Token.Window.Title:                           'bg:#95eaff #000046',Token.Window.TIItleV2:                         'bg:#9579fb #000046 bold',Token.AcceptMessage:                          'bg:#51ffff #004ca0',Token.ExitConfirmation:                       'bg:#00a6a0 #f0ffff',}
cyan_4={    Token.LineNumber:'#24d4ce bg:#000073',    Token.Prompt:                                 'bold',    Token.Prompt.Dots:                            'noinherit',    Token.In:                                     'bold #0000fb',    Token.In.Number:                              '',    Token.Out:                                    '#00ff46',    Token.Out.Number:                             '#00ff46',    Token.Separator:                              '#95eaff',    Token.Toolbar.Search:                         '#7e1eff noinherit',    Token.Toolbar.Search.Text:                    'noinherit',    Token.Toolbar.System:                         '#7e1eff noinherit',    Token.Toolbar.Arg:                            '#7e1eff noinherit',    Token.Toolbar.Arg.Text:                       'noinherit',    Token.Toolbar.Signature:                      'bg:#954cff #000046',    Token.Toolbar.Signature.CurrentName:          'bg:#5100fb #f0ffff bold',    Token.Toolbar.Signature.Operator:             '#000046 bold',    Token.Docstring:                              '#51a6fb',    Token.Toolbar.Validation:                     'bg:#004c46 #7ed4ff',    Token.Toolbar.Status:                         'bg:#001e73 #7ed4ff',    Token.Toolbar.Status.BatteryPluggedIn:        'bg:#001e73 #001eff',    Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#001e73 #00d473',    Token.Toolbar.Status.Title:                   'underline',    Token.Toolbar.Status.InputMode:               'bg:#001e73 #7effff',    Token.Toolbar.Status.Key:                     'bg:#000046 #51a6fb',    Token.Toolbar.Status.PasteModeOn:             'bg:#00d4a0 #f0ffff',    Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#247973 #7ed4ff',    Token.Toolbar.Status.PythonVersion:           'bg:#001e73 #f0ffff bold',    Token.Aborted:                                '#51a6fb',    Token.Sidebar:                                'bg:#95eaff #000046',    Token.Sidebar.Title:                          'bg:#f079fb #f0ffff bold',    Token.Sidebar.Label:                          'bg:#95eaff #001e73',    Token.Sidebar.Status:                         'bg:#c2ffff #000046',    Token.Sidebar.Selected.Label:                 'bg:#001e73 #d9ffff',    Token.Sidebar.Selected.Status:                'bg:#004ca0 #f0ffff bold',    Token.Sidebar.Separator:                       'bg:#95eaff #f0ffff underline',    Token.Sidebar.Key:                            'bg:#95eaff #000046 bold',    Token.Sidebar.Key.Description:                'bg:#95eaff #000046',    Token.Sidebar.HelpText:                       'bg:#f0ffff #000046',    Token.History.Line:                          '',    Token.History.Line.Selected:                 'bg:#0000fb  #000046',    Token.History.Line.Current:                  'bg:#f0ffff #000046',    Token.History.Line.Selected.Current:         'bg:#51a6ff #000046',    Token.History.ExistingInput:                  '#51a6fb',    Token.Window.Border:                          '#950046',    Token.Window.Title:                           'bg:#95eaff #000046',    Token.Window.TIItleV2:                         'bg:#9579fb #000046 bold',    Token.AcceptMessage:                          'bg:#51ffff #004ca0',    Token.ExitConfirmation:                       'bg:#00a6a0 #f0ffff',    Token.LineNumber:                             '#24d4ce bg:#001e73',        Token.SearchMatch:                            '#f0ffff bg:#7e4ca0',        Token.SearchMatch.Current:                    '#f0ffff bg:#004cff',        Token.SelectedText:                           '#f0ffff bg:#7e79ce',        Token.Toolbar.Completions:                    'bg:#954cff #000046',        Token.Toolbar.Completions.Arrow:              'bg:#954cff #000046 bold',        Token.Toolbar.Completions.Completion:         'bg:#954cff #000046',        Token.Toolbar.Completions.Completion.Current: 'bg:#5100fb #f0ffff',        Token.Menu.Completions.Completion:            'bg:#954cff #000046',        Token.Menu.Completions.Completion.Current:    'bg:#5100fb #f0ffff',        Token.Menu.Completions.Meta:                  'bg:#684cff #000046',        Token.Menu.Completions.Meta.Current:          'bg:#7e00ff #000046',        Token.Menu.Completions.ProgressBar:           'bg:#7ed4ff',        Token.Menu.Completions.ProgressButton:        'bg:#000046',}
cyan_4={    Token.LineNumber:'#24d4ce bg:#000073',
Token.Prompt:                                 'bold',
Token.Prompt.Dots:                            'noinherit',
Token.In:                                     'bold #0000fb',
Token.In.Number:                              '',
Token.Out:                                    '#00ff46',
Token.Out.Number:                             '#00ff46',
Token.Separator:                              '#95eaff',
Token.Toolbar.Search:                         '#7e1eff noinherit',
Token.Toolbar.Search.Text:                    'noinherit',
Token.Toolbar.System:                         '#7e1eff noinherit',
Token.Toolbar.Arg:                            '#7e1eff noinherit',
Token.Toolbar.Arg.Text:                       'noinherit',
Token.Toolbar.Signature:                      'bg:#954cff #000046',
Token.Toolbar.Signature.CurrentName:          'bg:#5100fb #f0ffff bold',
Token.Toolbar.Signature.Operator:             '#000046 bold',
Token.Docstring:                              '#51a6fb',
Token.Toolbar.Validation:                     'bg:#004c46 #7ed4ff',
Token.Toolbar.Status:                         'bg:#001e73 #7ed4ff',
Token.Toolbar.Status.BatteryPluggedIn:        'bg:#001e73 #aaff55',
Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#001e73 #118800',
Token.Toolbar.Status.Title:                   'underline',
Token.Toolbar.Status.InputMode:               'bg:#001e73 #7effff',
Token.Toolbar.Status.Key:                     'bg:#000046 #51a6fb',
Token.Toolbar.Status.PasteModeOn:             'bg:#00d4a0 #f0ffff',
Token.Toolbar.Status.PseudoTerminalCurrentVariable:'bg:#247973 #7ed4ff',
Token.Toolbar.Status.PythonVersion:           'bg:#001e73 #f0ffff bold',
Token.Aborted:                                '#51a6fb',

Token.Sidebar:                                'bg:#95eaff #000046',
Token.Sidebar.Title:                          'bg:#f079fb #f0ffff bold',
Token.Sidebar.Label:                          'bg:#95eaff #001e73',
Token.Sidebar.Status:                         'bg:#c2ffff #000046',
Token.Sidebar.Selected.Label:                 'bg:#001e73 #d9ffff',
Token.Sidebar.Selected.Status:                'bg:#004ca0 #f0ffff bold',
Token.Sidebar.Separator:                       'bg:#95eaff #f0ffff underline',
Token.Sidebar.Key:                            'bg:#95eaff #000046 bold',
Token.Sidebar.Key.Description:                'bg:#95eaff #000046',
Token.Sidebar.HelpText:                       'bg:#a0f0ff #000046',

Token.History.Line:                          '',
Token.History.Line.Selected:                 'bg:#0000fb  #000046',
Token.History.Line.Current:                  'bg:#f0ffff #000046',
Token.History.Line.Selected.Current:         'bg:#51a6ff #000046',
Token.History.ExistingInput:                  '#51a6fb',
Token.Window.Border:                          '#950046',
Token.Window.Title:                           'bg:#95eaff #000046',
Token.Window.TIItleV2:                         'bg:#9579fb #000046 bold',
Token.AcceptMessage:                          'bg:#51ffff #004ca0',
Token.ExitConfirmation:                       'bg:#00a6a0 #f0ffff',
Token.LineNumber:                             '#24d4ce bg:#001e73',
Token.SearchMatch:                            '#f0ffff bg:#7e4ca0',
Token.SearchMatch.Current:                    '#f0ffff bg:#004cff',
Token.SelectedText:                           '#f0ffff bg:#7e79ce',

Token.Toolbar.Completions:                    'bg:#954cff #000046',
Token.Toolbar.Completions.Arrow:              'bg:#954cff #000046 bold',
Token.Toolbar.Completions.Completion:         'bg:#954cff #000046',
Token.Toolbar.Completions.Completion.Current: 'bg:#5100fb #f0ffff',
Token.Menu.Completions.Completion:            'bg:#954cff #000046',
Token.Menu.Completions.Completion.Current:    'bg:#5100fb #f0ffff',
Token.Menu.Completions.Meta:                  'bg:#684cff #000046',
Token.Menu.Completions.Meta.Current:          'bg:#7e00ff #000046',
Token.Menu.Completions.ProgressBar:           'bg:#7ed4ff',
Token.Menu.Completions.ProgressButton:        'bg:#000046',
}





