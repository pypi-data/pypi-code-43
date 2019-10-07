from PyVoice.MyDict import MyDict, DictProperty


class SimpleResponse(MyDict):
    """
    {
      "textToSpeech": string,
      "ssml": string,
      "displayText": string,
    }
    """
    text_to_speech: str = DictProperty('textToSpeech', str)
    ssml: str = DictProperty('ssml', str)
    display_text: str = DictProperty('displayText', str)

    def build(self, text_to_speech: str = None, ssml: str = None, display_text: str = None):
        if text_to_speech is not None:
            self.text_to_speech = text_to_speech
        if ssml is not None:
            self.ssml = ssml
        if display_text is not None:
            self.display_text = display_text
        return self
