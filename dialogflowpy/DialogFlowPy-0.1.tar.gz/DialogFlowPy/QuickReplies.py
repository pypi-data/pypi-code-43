from typing import List
from PyVoice.MyDict import MyDict, DictProperty


class QuickReplies(MyDict):
    """
    {
      "title": string,
      "quickReplies": [
        string
      ]
    }
    """

    title: str = DictProperty('title', str)
    quick_replies: List[str] = DictProperty('quickReplies', list)

    def build(self, title: str, *quick_replies: str):
        self.title = title
        for item in quick_replies:
            self.quick_replies.append(item)

        return self

    def add_quick_replies(self, *quick_replies: str) -> List[str]:
        if self.quick_replies is None:
            self.quick_replies = []
        for item in quick_replies:
            self.quick_replies.append(item)

        return self.quick_replies
