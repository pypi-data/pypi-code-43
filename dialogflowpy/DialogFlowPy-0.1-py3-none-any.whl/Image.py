from PyVoice.MyDict import MyDict, DictProperty


class Image(MyDict):
    """
    {
      "imageUri": string,
      "accessibilityText": string
    }
    """
    uri : str = DictProperty('imageUri', str)
    accessiblity_test: str = DictProperty('accessibilityText', str)


    def build(self, uri: str=None, accessibility_text: str=None):
        if uri is not None:
            self.url = uri
        if accessibility_text is not None:
            self.accessibility_text = accessibility_text

        return self
