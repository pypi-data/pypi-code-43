from .filemodel import FileModel
import re
import base64


class CSS(FileModel):
    fontRegex = "src: *url\\('.*\\.ttf.*"

    def true_type_to_base64(self):
        """
        Replaces the path to the fontfile with the BASE64 encoded file.
        """
        fonts = re.findall(self.fontRegex, self.content)
        for item in fonts:
            file_name = item[item.find("url(\'") + 5:item.find(".ttf")+4]
            with open(self.rootDir + file_name, "rb") as font_file:
                font_file_content = font_file.read()
                encoded_string = base64.b64encode(font_file_content)
                font_file.close()
            self.content = self.content.replace("\'"+file_name+"\'", "data:font/ttf;base64,"+str(encoded_string))
