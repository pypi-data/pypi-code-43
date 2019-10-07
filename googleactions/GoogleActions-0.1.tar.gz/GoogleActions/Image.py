from PyVoice.MyDict import MyDict, DictProperty


class Image(MyDict):
    """
    {
      "url": string,
      "accessibilityText": string,
      "height": number,
      "width": number,
    }
    """
    url : str = DictProperty('url', str)
    accessiblity_test: str = DictProperty('accessibilityText', str)
    height: int = DictProperty('height', int)
    width: int = DictProperty('width', int)

    def build(self, url: str=None, accessibility_text: str=None, height: int=0, width: int=0):
        if url is not None:
            self.url = url
        if accessibility_text is not None:
            self.accessibility_text = accessibility_text
        if height is not None:
            self.height = height
        if width is not None:
            self.width = width
        return self
