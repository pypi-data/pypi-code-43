# -*- coding: utf-8 -*-
# @Time     : 2019/10/4 1:51
# @Author   : Run 
# @File     : transform.py
# @Software : PyCharm


from RunToolkit.for_str import split_to_words


def camel(s: str) -> str:
    """
    Converts a string to camelcase.
    """
    tmp = ' '.join(split_to_words(s)).title().replace(' ', '')
    return tmp[0].lower() + tmp[1:]
    

def kebab(s: str) -> str:
    """
    Converts a string to kebab case.
    Break the string into lowercase words and combine them with `-`.
    """
    return '-'.join(split_to_words(s)).lower()


def snake(s: str) -> str:
    """
    Converts a string to snake case.
    Break the string into lowercase words and combine them with `_`.
    """
    return '_'.join(split_to_words(s)).lower()


if __name__ == "__main__":
    print(camel('some_database_field_name'))  # 'someDatabaseFieldName'
    print(camel('Some label that needs to be camelized'))  # 'someLabelThatNeedsToBeCamelized'
    print(camel('some-javascript-property'))  # 'someJavascriptProperty'
    print(camel('some-mixed_string with spaces_underscores-and-hyphens'))  # 'someMixedStringWithSpacesUnderscoresAndHyphens'
    print(camel('AllThe-small Things'))
    print()

    print(kebab('camelCase'))  # 'camel-case'
    print(kebab('some text'))  # 'some-text'
    print(kebab('some-mixed_string With spaces_underscores-and-hyphens'))  # 'some-mixed-string-with-spaces-underscores-and-hyphens'
    print(kebab('AllThe-small Things'))
    print()

    print(snake('camelCase'))  # 'camel_case'
    print(snake('some text'))  # 'some_text'
    print(snake('some-mixed_string With spaces_underscores-and-hyphens'))  # 'some_mixed_string_with_spaces_underscores_and_hyphens'
    print(snake('AllThe-small Things'))  # "all_the_smal_things"
    print()
