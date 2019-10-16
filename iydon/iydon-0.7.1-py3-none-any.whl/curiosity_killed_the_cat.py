#!/usr/bin/env python
# coding: utf-8
'''*Just when you thought, Python could not be more fun.*
'''
__all__ = ('references', 'hello_world', 'zen', 'antigravity_comics', 'braces', 'cool_identifier', 'FLUFL', 'InPynite',
	'not_for_the_faint_of_heart')
def __dir__() -> list: return __all__


from .models import DemoCode


references = ('https://github.com/greyli/shedan',
	'https://github.com/OrkoHunter/python-easter-eggs')

hello_world = DemoCode(
	'import __hello__',
	'- 在 Python 中打印「Hello, World!」最简单的方式。')

zen = DemoCode(
	'import this',
	'- Python 设计哲学与代码风格指南。\n' \
	'- 《Python 之禅》在 PEP 20 中引入，它本应该是 20 条格言，' \
	'但是最终只写了 19 条，也许只是为了说明在文件的结尾总是应该保留一个空行。')

antigravity_comics = DemoCode(
	'import antigravity',
	'- 这会打开这个 xkcd 漫画，漫画展示了 Python 有多么简单易学。')

braces = DemoCode(
	'from __future__ import braces',
	'- 这用来快速结束任何关于在 Python 中引入大括号的讨论——不可能！')

cool_identifier = DemoCode(
	'from math import pi\n' \
	'π = pi',
	'- Python 3 中支持使用 Unicode 字符作为变量名。尽管如此，使用非英文字符作为变量名' \
	'可能不是一个好主意，不过它确实会让处理科学公式的工作变得更有意思。')

FLUFL = DemoCode(
	'from __future__ import barry_as_FLUFL\n' \
	'1 <> 2',
	'- 在认识到 Python 3.0 的不等运算符（!=）非常糟糕，是手指疼痛导致的错误后，' \
	'FLUFL（指 Uncle Barry）重新恢复钻石型操作符（<>）作为唯一的不等运算符拼写。\n' \
	'- PEP 401 是一个愚人节玩笑（从编号可以看出来）。这个 PEP 声明 Guido van Rossum 要退休了。他会获得一个新的头衔，' \
	'叫做「BDEVIL」（Benevolent Dictator Emeritus Vacationing Indefinitely from the Language，' \
	'去度无限期语言假期的仁慈退休独裁者），接任者将会是 Barry Warsaw（即 Uncle Barry），' \
	'Uncle Barry 的官方头衔是「FLUFL」（Friendly Language Uncle For Life，终生友好语言叔叔）。')

InPynite = DemoCode(
	'infinity = float("infinity")\n' \
	'print(hash(infinity))',
	'- 在 Python3 中，`hash(float("-inf"))` 将会生成 -10^5 x π，而在 Python 2 中则是 -271828（即 10^5 x e）。')

not_for_the_faint_of_heart = DemoCode(
	'import types\n' \
	'help(types.CodeType)',
	'- 如果你开始钻进 Python 的内部，你会在 help 输出看到一个关于 `types.CodeType` 的警告：不适合心脏脆弱者。')
