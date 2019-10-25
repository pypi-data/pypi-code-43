import os
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif(image_file):
  ret = {}
  i = Image.open(image_file)
  info = i._getexif()
  for tag, value in info.items():
    decoded = TAGS.get(tag, tag)
    ret[decoded] = value
  return ret
