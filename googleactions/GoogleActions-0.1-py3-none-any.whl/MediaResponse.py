from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from . import MediaType
from .MediaObject import MediaObject
from .Image import Image


class MediaResponse(MyDict):
    """
    {
      "mediaType": enum(MediaType),
      "mediaObjects": [
        {
          object(MediaObject)
        }
      ]
    }
    """
    media_type: MediaType = DictProperty('mediaType', MediaType)
    media_objects: List[MediaObject] = DictProperty('mediaObjects', list)

    def build(self, media_type: MediaType, *objects: MediaObject):

        for media_object in objects:
            self.media_objects.append(media_object)

        self.media_type = media_type

        return self

    def add_media_objects(self, *objects: MediaObject) -> List[MediaObject]:
        for item in objects:
            self.media_objects.append(item)

        return self.media_objects

    def add_media_object(self, name: str, description: str = None, content_url: str = None, image_url: str = None,
                         image_text: str = None, image_height: int = 0, image_width: int = 0, icon_url: str = None,
                         icon_text: str = None, icon_height: int = 0, icon_width: int = 0) -> MediaObject:

        media_object = MediaObject().build(name=name, description=description, content_url=content_url,
                                           large_image=Image().build(url=image_url, accessibility_text=image_text,
                                                                     height=image_height, width=image_width),
                                           icon=Image().build(url=icon_url,
                                                              accessibility_text=icon_text,
                                                              height=icon_height,
                                                              width=icon_width))
        self.media_objects.append(media_object)
        return media_object
