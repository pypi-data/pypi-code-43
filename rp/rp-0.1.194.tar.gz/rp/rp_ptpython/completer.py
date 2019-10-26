from __future__ import unicode_literals

from rp.prompt_toolkit.completion import Completer, Completion
from rp.prompt_toolkit.document import Document
from rp.prompt_toolkit.contrib.completers import PathCompleter
from rp.prompt_toolkit.contrib.regular_languages.compiler import compile as compile_grammar
from rp.prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter

from rp.rp_ptpython.utils import get_jedi_script_from_document
# from rp import printed,fansi_print
import re

__all__ = (
    'PythonCompleter',
)


class PythonCompleter(Completer):
    """
    Completer for Python code.
    """
    def __init__(self, get_globals, get_locals):
        super(PythonCompleter, self).__init__()

        self.get_globals = get_globals
        self.get_locals = get_locals

        self._path_completer_cache = None
        self._path_completer_grammar_cache = None

    @property
    def _path_completer(self):
        if self._path_completer_cache is None:
            self._path_completer_cache = GrammarCompleter(
                self._path_completer_grammar, {
                    'var1': PathCompleter(expanduser=True),
                    'var2': PathCompleter(expanduser=True),
                })
        return self._path_completer_cache

    @property
    def _path_completer_grammar(self):
        """
        Return the grammar for matching paths inside strings inside Python
        code.
        """
        # We make this lazy, because it delays startup time a little bit.
        # This way, the grammar is build during the first completion.
        if self._path_completer_grammar_cache is None:
            self._path_completer_grammar_cache = self._create_path_completer_grammar()
        return self._path_completer_grammar_cache

    def _create_path_completer_grammar(self):
        def unwrapper(text):
            return re.sub(r'\\(.)', r'\1', text)

        def single_quoted_wrapper(text):
            return text.replace('\\', '\\\\').replace("'", "\\'")

        def double_quoted_wrapper(text):
            return text.replace('\\', '\\\\').replace('"', '\\"')

        grammar = r"""
                # Text before the current string.
                (
                    [^'"#]                                  |  # Not quoted characters.
                    '''  ([^'\\]|'(?!')|''(?!')|\\.])*  ''' |  # Inside single quoted triple strings
                    "" " ([^"\\]|"(?!")|""(?!^)|\\.])* "" " |  # Inside double quoted triple strings

                    \#[^\n]*(\n|$)           |  # Comment.
                    "(?!"") ([^"\\]|\\.)*"   |  # Inside double quoted strings.
                    '(?!'') ([^'\\]|\\.)*'      # Inside single quoted strings.

                        # Warning: The negative lookahead in the above two
                        #          statements is important. If we drop that,
                        #          then the regex will try to interpret every
                        #          triple quoted string also as a single quoted
                        #          string, making this exponentially expensive to
                        #          execute!
                )*
                # The current string that we're completing.
                (
                    ' (?P<var1>([^\n'\\]|\\.)*) |  # Inside a single quoted string.
                    " (?P<var2>([^\n"\\]|\\.)*)    # Inside a double quoted string.
                )
        """

        return compile_grammar(
            grammar,
            escape_funcs={
                'var1': single_quoted_wrapper,
                'var2': double_quoted_wrapper,
            },
            unescape_funcs={
                'var1': unwrapper,
                'var2': unwrapper,
            })

    def _complete_path_while_typing(self, document):
        char_before_cursor = document.char_before_cursor
        return document.text and (
            char_before_cursor.isalnum() or char_before_cursor in '/.~')

    def _complete_python_while_typing(self, document):
        char_before_cursor = document.char_before_cursor
        return document.text and (
            char_before_cursor.isalnum() or char_before_cursor in '_.')

    def _get_completions(self, document, complete_event,force=False):# When force is true it acts like the original ptpython autocomplete
        force=True
        global old_origin,candidates
        origin=document.get_word_before_cursor()

        def yield_from_candidates(candidates:list):
            for c in candidates:
                yield Completion(text=c,start_position=-len(origin),display=c);
        import rp.r_iterm_comm as ric
        before_line=document.current_line_before_cursor
        import re
        # if re.fullmatch(r'.*[^\w\.]',before_line):
        #     yield from yield_from_candidates(list(ric.globa))
        #     # from rp import play_tone
        #     # play_tone(880,seconds=.03)  
        #     return
        blr=before_line[::-1]#blr=before_line reversed
        if '.' in blr:#This is a hack to make completions to namespaces like np.* not need to use jedi (which takes about 1 second to make a script which is super slow). This is a hack but it makes completions that would otherwise have to use jedi over 20x faster.
            found=re.match(r'(\.\w*[a-zA-Z_])+',blr[blr.find('.'):])
            if not found:
                pass#Something went wrong whatever
            elif found.string:
                found=found.string
                assert found,'wat? found='+repr(found.match)
                prefix=found[1:][::-1]
                try:
                    def keys(root):
                        out=set()
                        try:out.update(dir(root))
                        except:pass
                        try:out.update(root.__dict__)
                        except:pass
                        return sorted(out)
                    def evall():
                        parts=prefix.split('.')
                        cursor=ric.globa[parts[0]]
                        for part in parts[1:]:
                            cursor=getattr(cursor,part)
                        return cursor
                    yield from yield_from_candidates(keys(evall()))
                    # yield from yield_from_candidates(keys(eval(prefix,ric.globa)))
                    # from rp import play_tone
                    # play_tone(seconds=.03)
                    # print("HI"+repr(prefix)+"BYE")
                    return
                except Exception as E:
                    # from rp import print_stack_trace
                    # print_stack_trace(E)
                    #This type of error is perfectly normal and is to be expected.
                    #  ⮤ adsfpor.print_stack_trace: ERROR: Traceback (most recent call last):
                    #   File "/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/rp/rp_ptpython/completer.py", line 136, in _get_completions                                                                                     
                    #     yield from yield_from_candidates(keys(eval(prefix,ric.globa)))                                  
                    #   File "<string>", line 1, in <module>                                                              
                    # NameError: name 'adsfpo' is not defined  
                    pass#Oh well whatevs we'll do it with jedi, it will just be a bit slower


        # ric.current_candidates.clear()
        # if not origin:
        #     return
        if old_origin not in origin or force:# Make things faster when we're just adding on to a previous autocomplete thing by reusing our previous autocomplete data

            """
            Get Python completions.
            """
            # Do Path completions
            if complete_event.completion_requested or self._complete_path_while_typing(document):
                for c in self._path_completer.get_completions(document, complete_event):
                    # ric.current_candidates.append(c)
                    yield c

            # If we are inside a string, Don't do Jedi completion.
            import rp
            if self._path_completer_grammar.match(document.text_before_cursor):
                rp.r_iterm_comm.writing_in_string=True
                return
            rp.r_iterm_comm.writing_in_string=False

            # Do Jedi Python completions.
            if complete_event.completion_requested or self._complete_python_while_typing(document):
                doc=Document(document.text,document.cursor_position-(origin[::-1].find('.') if '.' in origin else len(origin)),document.selection)
                script = get_jedi_script_from_document(doc, self.get_locals(), self.get_globals())
                pos=document.cursor_position-len(origin)+1
                if script:
                    try:completions = script.completions()
                    except:pass#The original ptpython has a whole string of specific error types, and it looks like visual clutter. I got rid of it to see my code more easily. I dont think im missing much.
                    else:
                        # fff=1
                        for c in completions:
                            # if fff:
                                # from rp import ring_terminal_bell
                                # ring_terminal_bell()
                                # fff=0
                            thingy=Completion(c.name_with_symbols, len(c.complete) - len(c.name_with_symbols),display=c.name_with_symbols)
                            yield thingy
                        # else:
                            # from rp import ring_terminal_bell
                        return
                        candidates={c.name_with_symbols for c in completions}
                else:
                    print("ATTENTION: THIS HAS NEVER HAPPENED BEFORE, in completer.py")
                candidates=set(candidates)
                # if not force:
                #     candidates|=set(self.get_globals())|set(self.get_locals())# The namespace we search for completions in
        candidates =ryan_completion_matches(origin,tuple(candidates))    # Now its a list, and we've ordered our search.
        for c in candidates:
            # ric.current_candidates.append(c);
            yield Completion(text=c,start_position=-len(origin),display=c);
        else:
            from rp import is_namespaceable
            if not force and (not is_namespaceable(origin) or not origin):
                for x in self.get_completions(Document(document.text,document.cursor_position-len(origin)+(1 and len(origin)),),complete_event,force=True):
                    # ric.current_candidates.append(x);
                    yield x;# For when we want autocompletins for 'np.' or 'rinsp.' or 'rp.' etc, as opposed to 'pr' to print or 'lis' to list
        # if not force and not ric.current_candidates or origin not in old_origin and origin!=old_origin:old_origin=origin;return self.get_completions(document, complete_event,force=True)

        old_origin=origin
    def get_completions(self, document, complete_event,force=False):


        global completion_cache_pre_origin_doc
        from rp import tic,toc,ptoctic,ptoc 
        tic()
        origin=document.get_word_before_cursor()
        import rp.r_iterm_comm as ric
        pre_origin_doc=document.text[:document.cursor_position-(origin[::-1].find('.') if '.' in origin else len(origin))]
        from rp import ring_terminal_bell
        # if pre_origin_doc.endswith('.'):
            # ring_terminal_bell()
        # print()
        # print(pre_origin_doc)
        # print()
        flag=False
        while True:
            if pre_origin_doc not in completion_cache_pre_origin_doc or flag:
                ric.current_candidates=[]
                from rp import tic,ptoctic
                # tic()
                for c in self._get_completions(document, complete_event,force=False):
                    # print(c.text)
                    # print(c.text)
                    ric.current_candidates.append(str(c.text))
                # ptoctic()
                completion_cache_pre_origin_doc[pre_origin_doc]=tuple(ric.current_candidates)
                break
            else:
                ric.current_candidates=list(completion_cache_pre_origin_doc[pre_origin_doc])
                if not ric.current_candidates:
                    from rp import ring_terminal_bell
                    flag=True
                    # ring_terminal_bell()
                    continue

                else:
                    break
        # print("TIME1:",end='')
        # ptoc()
        # print()
        # print(ric.current_candidates)
        post_period_origin=origin if '.' not in origin else origin[origin.find('.')+1:]
        ric.current_candidates=ryan_completion_matches(post_period_origin,tuple(ric.current_candidates))
        # if '.' in origin:
            # ric.current_candidates==ric.current_candidates[::-1]

        for x in ric.current_candidates:
            if not x.startswith('_'):#Make sure things starting with '_' come last...
                yield Completion(text=x,start_position=-len(post_period_origin),display=x)
        for x in ric.current_candidates:
            if     x.startswith('_'):
                yield Completion(text=x,start_position=-len(post_period_origin),display=x)
        # print("TIME2:",end='')
        # ptoc()
        # print()

        # return ric.current_candidates

completion_cache_pre_origin_doc={}#Using a bit of dynamic programming to speed up autocompletion by A FACTOR OF 7!! (I measured it with the commented tics/tocs)
#region Time for some super-speedy optimization tricks...
old_origin=''
candidates=set()

from functools import lru_cache

_ryan_completion_matches_cache={}#Note: over time this might cause a memory leakage....idk if that will be a problem....
def ryan_completion_matches(origin:str,candidates:list):
    import rp
    #This function accomplishes one of the few **beautiful** things in rp.pseudo_terminal: my string matching algorithm, specifically made for python namespace elements
    # Better autocompletions
    # candidates origin is string
    # candidates is list of strings
    # def is_match(origin:str,candidate:str):
    #     origin   =list(origin   )# So we can pop chars
    #     candidate=list(candidate)
    #     while origin and candidate:
    #         if origin[0]==candidate.pop(0):
    #             origin.pop(0)
    #     return not origin
    h=hash(origin),hash(candidates)
    if h in _ryan_completion_matches_cache:
        # print(end="HAHA");rp.ptoc()

        return _ryan_completion_matches_cache[h]

    candidates=list(candidates)

    def match(origin:str,candidate:str)->int:
        # from rp import regex_match
        # if not candidate.strip():
            # return None
        # try:
        # import regex
        # if origin and not :#Optimization to quickly weed out most candidates
            # return None
        # except:
            # print("ERROR AT origin",candidate)

        temp=candidate
        origin   =list(origin   )# So we can pop chars
        candidate=list(candidate)
        out=.001
        count=0# higher count means worse match
        def match_char(a:str,b:str):
            return a.upper()==b.upper()
        while origin and candidate:
            pop=candidate.pop(0)
            if match_char(origin[0],pop):
                org=origin.pop(0)
                if org!=pop:
                    count+=.0001# small penalty for wrong char case. still keep it but dont give it ordering priority
                out+=count
                count=0
            elif pop in '_':
                count=0
                out+=.1# penalty because 'ab' is closer to 'a_bz' than 'az_b'
            else:
                count+=1
        import rp.r_iterm_comm
        # rp.tic()
        try:
            temp=(''.join(rp.r_iterm_comm.successful_commands)).count(temp)
            if temp:
                out/=temp# Doesn't have to be division; this is arbitrary. Basically, if we used this before successfully give it more weight and likelyness we want to use it again
        except AttributeError:pass# AttributeError: module 'rp.r_iterm_comm' has no attribute 'successful_commands'
        except TypeError:pass# TypeError: unsupported operand type(s) for /=: 'float' and 'str'
        # rp.ptoc()
        return None if origin else out
    c=candidates
    o=origin
    import rp
    # print('co',len(c),len(o))
    import re
    compiled=re.compile('.*'+'.*'.join(re.escape(x) for x in origin.lower())+'.*')#Using regex to weed out bad candidates sped this function up by an order of magnitude when we had 4000 candidates
    c=candidates=[c for c in candidates if compiled.fullmatch(c.lower())]#Speed things up and weed out bad candidates
    out=sorted([x[1] for x in sorted(x for x in zip([match(o,x)for x in c],c) if x[0] is not None) if x[1] is not 'mro'],key=lambda x:x==x.startswith('_')+(x.startswith('__') and x.endswith('__')))
    # rp.ptoc()
    _ryan_completion_matches_cache[h]=out
    return out
 