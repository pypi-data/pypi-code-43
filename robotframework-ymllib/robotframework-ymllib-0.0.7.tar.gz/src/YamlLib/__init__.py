from .edityaml import EditYML
from .error import CheckError


class YamlLib(object):
    def __init__(self):
        self._edit = EditYML()

    def yaml_search_the_word(self, path, word):
        """Search a ``word`` in yaml code.

        *Examples*
        
        | `Yaml Search The Word` | ${CURDIR}${/}file.yml | your word |
        """
        return self._edit.search_word(path, word)

    def yaml_update_words(self, path, before, after):
        """You can update the words in the file yml and save it

        *Examples*
        
        | `Yaml update words` | ${CURDIR}${/}file.yml | word to change | new word |
        """
        self._edit.change_words(path, before, after)

    def yaml_update_first_word(self, path, before, after):
        """You can update the first word in the file yml and save it

        *Examples*
        
        | `Yaml update first word` | ${CURDIR}${/}file.yml | word to change | new word |
        """
        self._edit.change_first_word(path, before, after)

    def yaml_update_near_argument(self, path, argument, value):
        """You can update the words near at argument in the file yml and save it

        *Examples*
        
        | `Yaml update words` | ${CURDIR}${/}file.yml | argument word | new word |
        """
        self._edit.change_after_the_allocation(path, argument, value)    

    def yaml_copy_file(self, path, name_copy):
        """Copy the yml file and add a name to your new copy.

        *Examples*
        
        | `Yaml copy file` | ${CURDIR}${/}file.yml | new name |
        """
        self._edit.copy_file_yml(path, name_copy)

    def yaml_append_part(self, path, row, part):
        """ Add a part of yaml code below your prefer row

        *Examples*
        
        | `Yaml append part` | ${CURDIR}${/}file.yml | 3 | your_api:${\\n}  address: 1.2.3.4${\\n}  port: 1234${\\n} |
        """
        self._edit.append_row_below(path, row, part)

    def yaml_remove_from_to(self, path, previous_number, next_number):
        """ Remove a part of the code

            *Examples*
            
        | `Yaml remove from to` | ${CURDIR}${/}file.yml | 1 | 5 |
        """
        self._edit.remove_rows(path, previous_number, next_number)