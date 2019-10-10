import json, glob, os, re
from typing import Any, Tuple, List, Dict
from lxml import etree

def json_read_to_object(input_file: str) -> Dict:
    '''
    Parses a valid JSON file to a python dict.
    :param input_file:
    :return: a dict object
    '''
    with open(input_file, 'r') as f:
        json_dict = json.load(f)
    return json_dict

def get_file_list_by_ext(dir: str, ext: Tuple[str], recursive: bool = False) -> List[str]:
    '''
    Takes a directory and uses `glob` to grab all files of provided extensions.
    :param dir: directory to scan
    :param ext:
    :param recursive: is search recursive? Works on Python 3.5+ only
    :return: a list of paths (abs or relative depends on input) to matching files
    '''
    if dir is None:
        raise("Directory for grabbing files from is not provided")
    if ext is None:
        raise("Extensions should be provided: ext=('jpg','png')")
    ext_formatted = []
    for ex in ext:
        ex = ex
        if ex.startswith('.'):
            ex = ex[1:]
        if not ex:
            continue
        ext_formatted.append(ex)

    if not ext_formatted:
        raise("No extensions left after formatting. Provide in format ext=('jpg','png')")

    ext = tuple(ext_formatted)
    if dir.endswith('/'):
        dir = dir[:-1]
    types_masks = ["{}/{}*.{}".format(dir,'**/' if recursive else '', x) for x in ext]
    result_list = []
    for type_mask in types_masks:
        result_list.extend(glob.glob(type_mask,recursive=recursive))
    return result_list

def cut_extension(file_path: str, long_extensions: Tuple[str] = ('tfrecord','pbtxt')) -> str:
    '''
    Cuts extension from filename (SHOULD BE [0;4] symbols or in the list of long_extensions (tuple of strings)).
    Relays on os.path.splittext logic.
    Examples:
    file.jpg => file
    /home/file. => /home/file
    /home/file.big_extension => /home/file.big_extension (unless it's in long_extensions)
    Default: file.tfrecord => file (since 'tfrecord' is in default long_extensions)
    :param file_path:
    :return:
    '''
    base, ext = os.path.splitext(file_path)
    if ext is not None and len(ext) > 5:
        if ext[1:] not in long_extensions:
            #it's not extension!
            return file_path
    return base

def dataset_filename_to_key(file_path: str) -> str:
    file_name = os.path.basename(file_path)
    key = cut_extension(file_name)
    return key


def pbmap_read_to_dict(input_file: str) -> Dict[int, str]:
    with open(input_file) as f:
        protobuf = f.read()
        indx2label = {}
        #parsed = re.findall(r'{[^}]+}', protobuf, re.U)
        names = re.findall(r"name: '([^']+)'", protobuf)
        ids = re.findall(r"id: (\d+)", protobuf)
        for id,name in zip(ids,names):
            indx2label[int(id)] = name

        if indx2label is None:
            raise Exception("Cannot parse labels file: {}".format(input_file))
        return indx2label


####XML

def parse_xml_pascalvoc(xml_path) -> Dict:
    '''
    Parses a valid XML file (which follows PascalVOC annotation) to a python dict.
    :param xml_path: path to the XML file with PascalVOC annotation for single image
    :return: a dictionary
    '''
    with open(xml_path, 'r') as file:
        xml_text = file.read()
    xml = etree.fromstring(xml_text)
    parse = recursive_parse_xml_to_dict(xml)
    return parse

def recursive_parse_xml_to_dict(xml):
  """Recursively parses XML contents to python dict.
  Credit: Object Detection API (TensorFlow)
  We assume that `object` tags are the only ones that can appear
  multiple times at the same level of a tree.

  Args:
    xml: xml tree obtained by parsing XML file contents using lxml.etree

  Returns:
    Python dictionary holding XML contents.
  """
  if xml is None or len(xml) == 0:
    return {xml.tag: xml.text}
  result = {}
  for child in xml:
    child_result = recursive_parse_xml_to_dict(child)
    if child.tag != 'object':
      result[child.tag] = child_result[child.tag]
    else:
      if child.tag not in result:
        result[child.tag] = []
      result[child.tag].append(child_result[child.tag])
  return {xml.tag: result}

def _mpath(path):
    '''
    Makes an absolute path from relative (related to module)
    :param path: path starting from syncvtools
    :return:
    '''
    dir_path = __file__
    dir_path = os.path.dirname(os.path.dirname(os.path.dirname(dir_path)))
    return os.path.join(dir_path,path)


if __name__ == "__main__":
    print(get_file_list_by_ext(dir='../examples/resources/pascalvoc/imgs/',
                               ext=('jpg', 'png', 'jpeg'),
                               recursive=True))
