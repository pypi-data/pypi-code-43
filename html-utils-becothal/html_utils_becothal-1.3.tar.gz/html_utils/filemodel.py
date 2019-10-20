
class FileModel:
    rootDir = ""
    sourceFileName = ""
    content = ""
    finalComment = "[finalComment]"

    def __init__(self):
        self.rootDir = ""
        self.sourceFileName = ""
        self.content = ""

    def read_file(self, filename):
        if filename == "":
            return
        self.extract_filename_and_root(filename)
        try:
            file_handler = open(self.rootDir + "/" + self.sourceFileName)
            self.content = file_handler.read()
            file_handler.close()
        except (OSError, IOError) as e:
            raise IOError(e.errno + e.errmessage)

    def to_string(self):
        """
        Returns the content of Object as String.
        :returns: Content of the Object as String
        :rtype: str
        """
        return self.content

    def extract_filename_and_root(self, filename):
        if filename == "":
            print("getRootPath: FileName was empty!")
            return
        filename.replace("\\", "/")
        self.sourceFileName = filename[filename.rfind('/') + 1:]
        self.rootDir = filename[:filename.rfind('/') + 1]

    def remove_comments(self, single_line_comment="", multi_line_comment_start="", multi_line_comment_end =""):
        """
        Removes all the comments from a file.
        :param single_line_comment: Tag for single line comment
        :param multi_line_comment_start: Start tag for a multi line comment
        :param multi_line_comment_end: End tag for a multi line comment
        :return: void
        """
        lines = self.get_content_in_lines()
        self.content = ""
        is_multi_line = False
        check_multi_line = False
        check_single_line = False
        if multi_line_comment_end != "" and multi_line_comment_start != "":
            check_multi_line = True
        if single_line_comment != "":
            check_single_line = True

        for i in range(len(lines)):
            if lines[i].find('\"') > -1 or lines[i].find('\'') > -1:
                self.content += lines[i] + "\n"
                continue
            if check_multi_line and not is_multi_line and lines[i].find(multi_line_comment_start) > -1:
                if lines[i].find(self.finalComment) > -1:
                    self.content += lines[i].replace(FileModel.finalComment, "") + "\n"
                else:
                    is_multi_line = True
                    if lines[i].find(multi_line_comment_end) > -1:
                        is_multi_line = False
                        temp = lines[i][lines[i].index(multi_line_comment_end) + len(multi_line_comment_end):]
                        self.content += lines[i][:lines[i].index(multi_line_comment_start)] + temp + "\n"
                    else:
                        self.content += lines[i][:lines[i].index(multi_line_comment_start)] + "\n"
            elif check_multi_line and is_multi_line:
                if lines[i].find(multi_line_comment_end) > -1:
                    is_multi_line = False
                    self.content += lines[i][lines[i].index(multi_line_comment_end) + len(multi_line_comment_end):] + "\n"

            elif check_single_line and lines[i].find(single_line_comment) > -1:
                if lines[i].find(self.finalComment) > -1:
                    self.content += lines[i].replace(self.finalComment, "") + "\n"
                else:
                    self.content += lines[i][:lines[i].index(single_line_comment)] + "\n"
            else:
                self.content += lines[i] + "\n"

    def get_content_in_lines(self):
        """
        This function converts the content into an array of lines.
        :return: content
        :rtype: array
        """
        lines = []
        if self.content == "":
            return lines
        lines = self.content.splitlines()
        return lines

    def uglify(self):
        """
        Removes all the `\n` from the file so the file becomes a single line.
        :return:
        """
        self.content = self.content.replace("\n", "")