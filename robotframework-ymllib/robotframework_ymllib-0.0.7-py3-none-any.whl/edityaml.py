import yaml
import shutil
import re
from .error import CheckError

class EditYML(object):

    def change_words(self, file_path, before, after):
        fileset = ''
        try:
            file_to_read = open(file_path, "r")
            with file_to_read as stream:
                for line in stream.readlines():
                    t = line.replace(before, after)
                    fileset += t
                file_to_write = open(file_path, "w")
                file_to_write.truncate(0)
                file_to_write.write(fileset)
                file_to_write.close()

        except yaml.YAMLError as exc:
            raise exc

    def change_first_word(self, file_path, before, after):
        fileset = ''
        try:
            isfirst = True
            with open(file_path, "r") as stream:
                for line in stream.readlines():
                    if line.find(before) >= 0 and isfirst == True:
                        t = line.replace(before, after, 1)
                        isfirst = False
                        print('dentro')
                    else:
                        t = line
                    fileset += t
                file_to_write = open(file_path, "w")
                file_to_write.truncate(0)
                file_to_write.write(fileset)
                file_to_write.close()

        except yaml.YAMLError as exc:
            raise exc   
    
    def change_after_the_allocation(self, file_path, argument, value):
        self.new_change = EditYML()
        word_found = self.new_change._search_argument(file_path, argument)
        self.new_change.change_first_word(file_path, word_found, value)

    
    def _search_argument(self, file_path, argument):
        with open(file_path, "r") as stream:
            for line in stream:
                obj = re.sub(r"\s+", "", line, flags=re.UNICODE)
                objwithspace = re.sub(r"\n", "", line, flags=re.UNICODE)
                if obj.startswith(argument+":"):
                    return objwithspace.split()[1]
                elif obj.startswith(argument+"="):
                    return objwithspace.split()[2]        
                    
    def remove_rows(self, file_path, previous_number, next_number):
        fileset = ''
        try:
            with open(file_path, "r") as stream:
                for k, line in enumerate(stream.readlines(), start=1):
                    if int(previous_number) <= k <= int(next_number):
                        fileset += line
            stream.close()
            with open(file_path, "a") as filemode:
                filemode.truncate(0)
                filemode.write(fileset)

        except yaml.YAMLError as exc:
            raise exc

    def append_row_below(self, file_path, number_rows, part):
        try:
            f = open(file_path, "r")
            line = f.readlines()
            f.close()
            line.insert(int(number_rows), part + "\n")

            f = open(file_path, "w")
            line = "".join(line)
            f.write(line)
            f.close()

        except yaml.YAMLError as exc:
            raise exc

    def search_word(self, file_path, word_to_check):
        try:
            with open(file_path, "r") as stream:
                result = EditYML()._how_many_times_this_word(stream, word_to_check)
                if result > 0:
                    return result
                else:
                    raise CheckError("{0} dosen't exist in {1}".format(word_to_check, file_path.split("/")[-1]))
        except yaml.YAMLError as exc:
            raise exc

    def _how_many_times_this_word(self, stream, word_to_check):
        count = 0
        for line in stream.readlines():
            count += line.lower().split().count(word_to_check)
        return count

    def copy_file_yml(self, file_path, new_name):
        dotyml = ".yml"
        copy_file_path = new_name + dotyml
        try:
            shutil.copyfile(file_path, copy_file_path)
        except yaml.YAMLError as exc:
            raise exc
