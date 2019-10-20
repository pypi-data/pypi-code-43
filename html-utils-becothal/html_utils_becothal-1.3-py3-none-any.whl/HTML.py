from .filemodel import FileModel
import re
import base64
from .CSS import CSS


class HTML(FileModel):

    cssRegex = "(<link rel=\"stylesheet\".* href=\".*\\.css\">)"
    jsRegex = "(<script.*src=\".*\"><\/script>)"

    def __init__(self):
        FileModel.__init__(self)

    def inline_css(self):
        """
        Searches for linked CSS files and copies the content into the HTML file,
        so that there is only one file in the end.
        """
        temp_string = ""
        if self.content == "":
            print("InlineCSS: cannot inline. File must be read first.")
            return
        css_files = re.findall(self.cssRegex, self.content)
        if len(css_files) > 0:
            i = 0
            for item in css_files:
                if i == 0:
                    temp_string = "<style>"

                css_file = CSS()
                css_file.read_file(self.rootDir + HTML.get_file_path_from_link(str(item)))
                css_file.remove_comments("", "/*", "*/")
                css_file.true_type_to_base64()
                temp_string += css_file.to_string()

                if i == len(css_files)-1:
                    temp_string += "</style>"

                self.content = self.content.replace(str(item), temp_string)

                temp_string = ""
                i += 1

    def inline_js(self):
        """
        Searches the HTML file for linked JavaScript files and inlines them to the HTML file.
        """
        temp_string = ""
        if self.content == "":
            print("inlineJS: cannot inline. Content is Empty. File must be read first")
            return
        js_files = re.findall(self.jsRegex, self.content)
        if len(js_files) > 0:
            i = 0
            for item in js_files:
                if i == 0:
                    temp_string = "<script>"
                js_file = FileModel()
                js_file.read_file(self.rootDir + HTML.get_file_path_from_link(str(item)))
                js_file.remove_comments("//", "/*", "*/")
                temp_string += js_file.to_string()
                if i == len(js_files)-1:
                    temp_string += "</script>"

                self.content = self.content.replace(str(item), temp_string)
                temp_string = ""
                i += 1

    def write_file(self, file_name):
        """
        Writes the content of the HTML-Object into a File
        :param file_name: Filename for the output file
        :type file_name: str
        """
        if file_name == "":
            print("writeFile: No FileName provided!")
            return
        else:
            file_handler = open(file_name, "w")
            file_handler.write(self.to_string())
            file_handler.close()

    def images_to_base64(self):
        """
        Converts the source for <img> tags to Base64.
        Only the following formats are possible:
         - bmp
         - gif
         - jpeg
         - png
         - svg
        :return:
        """
        mime_type = {
            "bmp": "bmp",
            "gif": "gif",
            "jpg": "jpeg",
            "jpe": "jpeg",
            "jpeg": "jpeg",
            "png": "png",
            "svg": "svg+xml"
        }
        image_regex = "<img.*src=.*"
        images = re.findall(image_regex, self.content)
        for item in images:
            file_name = item[item.find("src=") + 5:item.find("\"", item.find("src=") + 5)]
            if "data:image" in file_name:
                continue
            with open(self.rootDir + file_name, "rb") as imageFile:
                image_file_content = imageFile.read()
                encoded_string = base64.b64encode(image_file_content)
                imageFile.close()
            self.content = self.content.replace(file_name, "data:image/"
                + mime_type[file_name[file_name.rfind(".")+1:len(file_name)]] + ";base64," + str(encoded_string,'utf-8'))

    @staticmethod
    def get_file_path_from_link(link):
        """
        Returns the file_path for a file in a <link> in HTML
        :param link: <link> from HTML
        :type link: str
        :returns: file_path provided in the <link>
        :rtype: str
        """
        if link == "":
            print("getFilePathFromLink: No link provided")
            return
        file_path = ""
        if link.find("href=") > 0:
            file_path = link[link.find("href=\"") + 6:link.rfind("\"")]
        elif link.find("src=") > 0:
            file_path = link[link.find("src=\"") + 5:link.rfind("\"")]
        else:
            print("getFilePathFromLink: Unrecognized pattern :" + link)
            return
        return file_path
