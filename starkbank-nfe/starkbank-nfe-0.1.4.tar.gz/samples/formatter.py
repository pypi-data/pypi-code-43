# coding: utf-8
from sys import version
from nfe.utils.compatibility import String

print(version)

text = String.string("é {}, ná {}, lá {}")
la = String.string("lá")
na = String.string("ná")
print(text)
print(type(text))

parameters = {
    "é": text,
    "ná": na,
    "lá": la,
}


String.string(text)
String.stringFormat(parameters)

# def stringFormat(text, **kargs):
#     a = text.decode("utf-8").format({key: string(kargs[key])} for key in kargs)
#     return string(a)

# parameters = {
#     "name": "é",
#     "age": "a",
# }
# textWithFormat = string("{name} é {age}")

# a = string(text)
# type(a)
#
# b = stringFormat(textWithFormat, **parameters)
#
# print(a)
# print(b)
