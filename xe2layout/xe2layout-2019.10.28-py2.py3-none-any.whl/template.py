#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# @copyright Copyright (C) Guichet Entreprises - All Rights Reserved
# 	All Rights Reserved.
# 	Unauthorized copying of this file, via any medium is strictly prohibited
# 	Dissemination of this information or reproduction of this material
# 	is strictly forbidden unless prior written permission is obtained
# 	from Guichet Entreprises.
###############################################################################

###############################################################################
# Template generation for xenon2
###############################################################################

import logging
import os
import sys
import shutil
import re
import html5lib
from bs4 import BeautifulSoup
import jinja2
import polib
import json

import pymdtools.common as common

from . import config
from . import __init__ as initModule

###############################################################################
# Destination folders
# Folder with all resources
# This folder will be copied into the final website root
###############################################################################
__RESOURCES__ = "resources"

###############################################################################
# Destination folders
# Folder with all jinja files
###############################################################################
__JINJA__ = "jinja"

###############################################################################
# Destination folders
# Folder with all html jinja files
# This folder is build from the main_page
###############################################################################
__TEMPLATE__ = "template"

###############################################################################
# Destination folders
# Folder with all gettext files
###############################################################################
__LOCALE__ = "locale"

###############################################################################
# File with the context
###############################################################################
__CONTEXT_YML__ = "template_context.yml"

###############################################################################
# Singleton for template log handler
###############################################################################
@common.static(__handler__=None)
def template_log_handler(conf, action_add=None, action_del=None):
    if template_log_handler.__handler__ is None and action_add:
        log_filename = conf['paths']['template_destination']['log_filename']
        # print(log_filename)
        log_handler = logging.FileHandler(log_filename)
        log_handler.setLevel(logging.INFO)

        log_handler.setFormatter(
            logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s'))
        logging.getLogger('').addHandler(log_handler)
        template_log_handler.__handler__ = log_handler

    if template_log_handler.__handler__ is not None and action_del:
        logging.getLogger('').removeHandler(template_log_handler.__handler__)
        template_log_handler.__handler__ = None

    return template_log_handler.__handler__

###############################################################################
# Check list type
#
# @param data the data to check
# @return data or [data] in order to have a list
###############################################################################
def check_list_type(data):
    result = data
    if not isinstance(result, list):
        result = [result]
    return result

###############################################################################
# Clean the layout of the file. drop attributes
#
# @param xml_soup the BeautifulSoup object input
# @param attribute_part the attribute to change
# @return the BeautifulSoup object
###############################################################################
def remove_attributes(xml_soup, attribute_part):
    logging.info("Remove attribute %s", attribute_part)
    for tag in xml_soup.findAll():
        attr_to_remove = []
        for key in tag.attrs:
            if attribute_part in key:
                attr_to_remove.append(key)

        for key in attr_to_remove:
            tag.attrs.pop(key, None)
    return xml_soup

###############################################################################
# Clean the layout of the file. drop tags
#
# @param xml_soup the BeautifulSoup object input
# @param tag_name the tag name
# @return the BeautifulSoup object
###############################################################################
def remove_tags(xml_soup, tag_name):
    logging.info("Remove tag %s", tag_name)

    tag_to_remove = []

    def search_fun(tag):
        return tag.name == tag_name and not tag.attrs

    for tag in xml_soup.find_all(search_fun):
        tag_to_remove.append(tag)

    for tag in tag_to_remove:
        tag.decompose()

    return xml_soup

###############################################################################
# A decorator to read and transform xml file
#
# @param xml_transformation the BeautifulSoup transformation
# @return the wrapper
###############################################################################
def decorator_read_file_xml(xml_transformation):
    def wrapper(*args, **kwargs):
        for _unused_idx, arg in enumerate(args):
            filename = common.check_is_file_and_correct_path(arg)

            xml_content = common.get_file_content(filename)
            xml_soup = BeautifulSoup(xml_content, "html5lib")
            result = xml_transformation(xml_soup, **kwargs)
            common.set_file_content(filename, str(result), encoding="utf-8")

    return wrapper


###############################################################################
# Clean the layout of the file. drop tags
#
# @param html_layout the BeautifulSoup object input
# @return the BeautifulSoup object
###############################################################################
def remove_attributes_from_file(filename, **kwargs):
    decorator_read_file_xml(remove_attributes)(filename, **kwargs)


###############################################################################
# Clean the layout of the file. drop tags
#
# @param html_layout the BeautifulSoup object input
# @return the BeautifulSoup object
###############################################################################
def remove_tag_from_file(filename, **kwargs):
    decorator_read_file_xml(remove_tags)(filename, **kwargs)


###############################################################################
# Clean the layout of the file. Remove the th: namespace
#
# @return the filename of THIS script.
###############################################################################
def clean_html(filename, conf, backup_option=False):
    filename = common.check_is_file_and_correct_path(filename)

    # Create Backup
    if backup_option:
        common.create_backup(filename)

    # remove attributes
    rm_attrs = check_list_type(conf['layout']['clean']['remove_attributes'])
    for attribute in rm_attrs:
        remove_attributes_from_file(filename, attribute_part=attribute)

    # remove tags
    rm_tags = check_list_type(conf['layout']['clean']['remove_tags'])
    for tag in rm_tags:
        remove_tag_from_file(filename, tag_name=tag)

###############################################################################
# build all resources for template
#
# @param folder_input the input folder with all files
# @param folder_ouput the oupupt folder with all files proccessed
###############################################################################
def grab_resources(folder_input, folder_output, file_extension_to_copy):
    logging.info("Build resources from %s to %s", folder_input, folder_output)
    folder_input = common.check_folder(folder_input)

    # # clean the old folder
    # if os.path.isdir(folder_output):
    #     logging.info("Clean the output folder %s", folder_output)
    #     logging.debug('Delete folder : %s', folder_output)
    #     shutil.rmtree(folder_output)

    folder_output = common.check_create_folder(folder_output)
    folder_input = common.set_correct_path(folder_input)

    # ------------------------------------------------------------------------
    def copy_in_output(filename):
        input_filename = common.check_is_file_and_correct_path(filename)
        rel_path = os.path.relpath(input_filename, folder_input)
        output_filename = os.path.join(folder_output, rel_path)

        common.check_create_folder(os.path.split(output_filename)[0])
        shutil.copyfile(input_filename, output_filename)
        return output_filename
    # ------------------------------------------------------------------------

    for ext in file_extension_to_copy:
        logging.info("Copy files with extension %s", ext)
        common.apply_function_in_folder(folder_input, copy_in_output,
                                        filename_ext=ext)

###############################################################################
#
###############################################################################
def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        source = os.path.join(src, item)
        destin = os.path.join(dst, item)
        if os.path.isdir(source):
            copytree(source, destin, symlinks, ignore)
        else:
            if not os.path.exists(destin) or \
                    os.stat(source).st_mtime - os.stat(destin).st_mtime > 1:
                logging.info("Copy file %s -> %s", source, destin)
                shutil.copy2(source, destin)

###############################################################################
# compil one po file to mo file
#
# @param filename the po file
###############################################################################
def compile_po(filename):
    po_filename = common.check_is_file_and_correct_path(filename)
    mo_filename = common.filename_ext_to(filename, ".mo")

    if os.path.isfile(mo_filename):
        os.remove(mo_filename)

    podata = polib.pofile(po_filename)
    podata.save_as_mofile(mo_filename)


###############################################################################
# compil all po file in the folder
#
# @param conf the conf as a dict
###############################################################################
def compile_po_files(folder):
    common.apply_function_in_folder(folder, compile_po, filename_ext=".po")

###############################################################################
# Adjust images
#
# @param filename the image filename
###############################################################################
def configure_image(filename):
    filename = common.check_is_file_and_correct_path(filename)
    logging.info("Adjust the image %s", filename)

###############################################################################
# build all resources for template
#
# @param conf the conf as a dict
###############################################################################
def configure_resources(conf):
    conf_paths = conf['paths']
    folder_output = conf_paths['template_destination']['root']
    folder_resources = os.path.join(folder_output, __RESOURCES__)

    common.apply_function_in_folder(folder_resources, configure_image, ".png")
    common.apply_function_in_folder(folder_resources, configure_image, ".jpg")

###############################################################################
# build all resources for template
#
# @param conf the conf as a dict
###############################################################################
def build_common_resources(conf):
    conf_paths = conf['paths']
    folder_output = conf_paths['template_destination']['root']
    logging.info(">>> template_destination=%s", folder_output)

    other_res = {
        'res': {'key': 'additional_resources', 'dest': __RESOURCES__},
        'jinja': {'key': 'jinja_sources', 'dest': __JINJA__},
        'locale': {'key': 'locale_resources', 'dest': __LOCALE__},
    }

    # copy other folder
    for res_key in other_res:
        src_folder_list = check_list_type(
            conf_paths[other_res[res_key]['key']])

        folder_output_add_res = os.path.join(
            folder_output, other_res[res_key]['dest'])

        if os.path.isdir(folder_output_add_res):
            logging.debug('Delete folder : %s', folder_output_add_res)
            shutil.rmtree(folder_output_add_res)

        folder_output_add_res = common.check_create_folder(
            folder_output_add_res)

        for src_folder in src_folder_list:
            folder_add_src = common.check_folder(src_folder)
            copytree(folder_add_src, folder_output_add_res)

    # copy the specific resources from layout
    folder_input = conf_paths['layout_sources']
    folder_input = common.check_folder(folder_input)
    folder_output_res = os.path.join(folder_output, __RESOURCES__)
    file_extension_to_copy = conf['layout']['file_extensions_resources']

    logging.info(">>> layout_sources=%s", folder_input)
    grab_resources(folder_input, folder_output_res, file_extension_to_copy)

    # compile translation
    locale_folder = os.path.join(folder_output, other_res['locale']['dest'])
    logging.info(">>> Compile translation in the folder %s", locale_folder)
    compile_po_files(locale_folder)

###############################################################################
# replace with Xpath location
#
# @param filename the html filename
# @param re_start the begining token
# @param re_end the ending token
# @return the header tag
###############################################################################
def apply_function_in_html5(html5_content, location_xpath, transform):
    root = html5lib.parse(html5_content)  # , treebuilder="lxml")
    ns_dict = {}

    for attr in root.items():
        key = attr[0]
        if (len(key) >= 5) and (key[0:5] == "xmlns"):
            ns_dict[key] = attr[1]

    for key in ns_dict:
        location_xpath = location_xpath.replace("{" + key + "}",
                                                "{" + ns_dict[key] + "}")

    elements = root.findall(location_xpath)
    for element in elements:
        transform(element, root)

    result = html5lib.serialize(root, tree="etree",
                                encoding="utf-8",
                                omit_optional_tags=False,
                                quote_attr_values="always",
                                alphabetical_attributes=True)
    result = result.decode("utf-8")

    return result


###############################################################################
# replace with Xpath location
#
# @param filename the html filename
# @param re_start the begining token
# @param re_end the ending token
# @return the header tag
###############################################################################
def transform_content(html5_content, location_xpath,
                      set_content_text,
                      this_value, transform_dict):

    logging.info("xpath %s ==> %s", location_xpath, transform_dict)

    def local_transform(element, _unused_root):
        for key, value in transform_dict.items():
            if key == set_content_text:
                element.text = value
            else:
                real_value = value
                real_value = value.replace(this_value,
                                           element.get(key, default=""))
                element.set(key, real_value)

    return apply_function_in_html5(html5_content, location_xpath,
                                   local_transform)


###############################################################################
# remove tags
###############################################################################
def remove_content(html5_content, location_xpath):
    logging.info("Remove tag xpath %s ", location_xpath)

    def local_transform(element, _unused_root):
        element.clear()

    return apply_function_in_html5(html5_content, location_xpath,
                                   local_transform)

###############################################################################
#
###############################################################################
def insert_jinja_xml_tag(html5_content, location_xpath, jinja_filename):
    logging.info('insert tag jinja %s --> %s', location_xpath, jinja_filename)

    def local_transform(element, _unused_root):
        list_remove = [child for child in element]
        for child in list_remove:
            element.remove(child)
        new_el = element.makeelement("insertjinja",
                                     {"jinjafile": jinja_filename})
        element.insert(0, new_el)

    return apply_function_in_html5(html5_content, location_xpath,
                                   local_transform)


###############################################################################
# replace with Xpath location
# @param filename the html filename
###############################################################################
def prepare_main_page_html(filename, conf):
    filename = common.check_is_file_and_correct_path(filename)
    clean_html(filename, conf)
    html5_content = common.get_file_content(filename)

    # apply xpath transformation
    insert_tag = conf['layout']['transform_tag_attributes']
    this_value = conf['layout']['transform_tag_attributes_this']
    set_content_text = conf['layout']['transform_tag_attributes_set_content']

    for xpath in insert_tag:
        html5_content = transform_content(
            html5_content, xpath, set_content_text,
            this_value, insert_tag[xpath])

    common.set_file_content(filename, html5_content)

    # remove tags
    remove_tags_from_file = check_list_type(
        conf['layout']['remove_tags_from_xpath'])
    for xpath in remove_tags_from_file:
        html5_content = remove_content(html5_content, xpath)
    common.set_file_content(filename, html5_content)

    # some other change with regex
    replace_str = conf['layout']['replace_str']
    for key in replace_str:
        num = 0
        (html5_content, num) = re.subn(key, replace_str[key], html5_content)
        logging.info("replace %s -> %s", key, num)
    common.set_file_content(filename, html5_content)

    # locate the jinja2 part to insert
    insert_j2 = conf['layout']['insert_jinja']

    for xpath in insert_j2:
        html5_content = insert_jinja_xml_tag(
            html5_content, xpath, insert_j2[xpath])
    common.set_file_content(filename, html5_content)


###############################################################################
# replace with Xpath location
# @param filename the html filename
# @param re_start the begining token
# @param re_end the ending token
# @return the header tag
###############################################################################
def extract_part_html(filename, location_xpath, output_filename):
    logging.info('Extract xpath %s', location_xpath)
    filename = common.check_is_file_and_correct_path(filename)
    html5_content = common.get_file_content(filename)

    result_list = []

    # ------------------------------------------------------------------
    def collect_file(element, _unused_root):
        result = html5lib.serialize(element, tree="etree",
                                    encoding="utf-8",
                                    omit_optional_tags=False,
                                    quote_attr_values="always",
                                    alphabetical_attributes=True)
        result = result.decode("utf-8")
        result_list.append(result)
    # ------------------------------------------------------------------

    apply_function_in_html5(html5_content,
                            location_xpath, collect_file)

    if len(result_list) > 1:
        logging.error('Too many result in extraction')
        raise Exception('Too many result in extraction')

    if len(result_list) < 1:
        logging.error('No result in extraction XPath=%s', location_xpath)
        raise Exception('No result in extraction XPath=%s' % location_xpath)

    only_template_name = os.path.split(output_filename)[1]
    only_template_name = os.path.splitext(only_template_name)[0]

    template_content = """
{%%- if %(var)s_off is undefined -%%}
<!-- %(var)s_off is undefined -->
%(content)s
{%%- else -%%}
<!-- %(var)s_off is defined -->
{%%- endif -%%}
""" % {'var': only_template_name, "content": result_list[0]}

    common.set_file_content(output_filename, template_content, bom=False)

    # ------------------------------------------------------------------
    def remove_part(element, _unused_root):
        element.attrib.clear()
        element.set("xenon-template", only_template_name)
        list_remove = [child for child in element]
        for child in list_remove:
            child.clear()
            element.remove(child)
        element.text = ''
        # element.clear()
    # ------------------------------------------------------------------
    html5_content = apply_function_in_html5(html5_content,
                                            location_xpath, remove_part)

    common.set_file_content(filename, html5_content)


###############################################################################
# Find a jinja file in standard path
#
# @param filanme the filename searched
# @return the content of the file
###############################################################################
def get_jinja_content(filename, j2_folder):
    the_file = os.path.join(j2_folder, filename)
    the_file = common.check_is_file_and_correct_path(the_file)
    return common.get_file_content(the_file)

###############################################################################
# replace with Xpath location
# @param filename the html filename
# @param re_start the begining token
# @param re_end the ending token
# @return the header tag
###############################################################################
def insert_jinja_file_in_html(filename, j2_folder):
    logging.info('Jinja folder %s', j2_folder)
    logging.info('Insert jinja file in  %s', filename)
    filename = common.check_is_file_and_correct_path(filename)
    html5_content = common.get_file_content(filename)

    jinja_file_list = []

    # ------------------------------------------------------------------
    def collect_file(element, _unused_root):
        j2_file = element.get("jinjafile")
        if j2_file is not None:
            logging.info('Add jinja file in  %s', j2_file)
            jinja_file_list.append(j2_file)
    # ------------------------------------------------------------------

    apply_function_in_html5(html5_content,
                            ".//{http://www.w3.org/1999/xhtml}insertjinja",
                            collect_file)

    for j2_file in jinja_file_list:
        j2_content = get_jinja_content(j2_file, j2_folder)
        (html5_content, _unused) = re.subn(
            '<insertjinja jinjafile="%s"></insertjinja>' % j2_file,
            j2_content, html5_content)

    re_template = r"""<(?P<tag>[a-zA-Z0-9_-]+)""" \
        r"""\s+xenon-template="(?P<name>[^"]*?)">""" \
        r""".*?</(?P=tag)>"""

    replace_str = r"""\n{%- include "\g<name>.html" -%}\n"""

    (html5_content, _unused) = re.subn(re_template,
                                       replace_str, html5_content)

    common.set_file_content(filename, html5_content, bom=False)


###############################################################################
# build all resources for template
#
# @param conf the conf as a dict
###############################################################################
def build_template(conf):
    conf_paths = conf['paths']

    html_input = conf_paths['main_page']
    html_input = common.check_is_file_and_correct_path(html_input)
    logging.info("Main page source %s", html_input)

    folder_output = conf_paths['template_destination']['root']
    folder_output = os.path.join(folder_output, __TEMPLATE__)
    if os.path.isdir(folder_output):
        logging.info("Clean the output folder %s", folder_output)
        logging.debug('Delete folder : %s', folder_output)
        shutil.rmtree(folder_output)
    folder_output = common.check_create_folder(folder_output)
    logging.info("Template output %s", folder_output)

    main_page_filename = os.path.join(folder_output, "main_page.html")
    logging.info("Copy main page %s", main_page_filename)
    shutil.copyfile(html_input, main_page_filename)

    prepare_main_page_html(main_page_filename, conf)

    # extract part of the html and locate the extract
    # Explode the main page in small pieces
    j2_folder = conf_paths['template_destination']['root']
    j2_folder = common.check_folder(os.path.join(j2_folder, __JINJA__))
    main_page_partition = conf['layout']['main_page_partition']
    for xpath in main_page_partition:
        ouput_file = os.path.join(folder_output, main_page_partition[xpath])
        extract_part_html(main_page_filename, xpath, ouput_file)
        # finaly insert the jinja file inside
        insert_jinja_file_in_html(ouput_file, j2_folder)

    insert_jinja_file_in_html(main_page_filename, j2_folder)

    # Last step
    index_html = common.get_file_content(main_page_filename)
    index_html = conf['layout']['main_page_header'] + index_html

    common.set_file_content(main_page_filename, index_html)


###############################################################################
# build all resources for template
#
# @param conf the conf as a dict
###############################################################################
def create_doc(conf):
    conf_paths = conf['paths']['template_destination']

    folder_output = conf_paths['root']
    folder_output = common.check_folder(folder_output)

    main_page_partition = conf['layout']['main_page_partition']

    params = []
    for key in main_page_partition:
        logging.info("Add doc parameter %s", main_page_partition[key])
        params.append({
            "name": os.path.splitext(main_page_partition[key])[0],
            "filename": main_page_partition[key],
        })

    conf_content = common.get_file_content(conf['paths']['conf_filename'])
    raw_vars = re.findall(r'\{\{\w+\}\}', conf_content)
    vars_list = []
    for raw_var in raw_vars:
        element = raw_var[2:-2]
        if element not in vars_list:
            vars_list.append(element)

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(__get_this_folder(),
                                                    "templates")),
        autoescape=jinja2.select_autoescape(['html', 'xml']))

    template = template_env.get_template("readme.md.j2")
    doc_filename = os.path.join(folder_output,
                                conf_paths['result_parameters_filename'])

    with open(os.path.join(__get_this_folder(),
                           "..", "package.json")) as json_file:
        data = json.load(json_file)

    readme_content = template.render({
        "params": params,
        "vars": vars_list,
        "template_context": conf['context'],
        "version": data['version'],
        "author": data['author'],
        "copyright": data['copyright'],
        "url": data['url'],
        "package_name": conf['package_name'],
    })

    common.set_file_content(doc_filename, readme_content)

    # generate template conf for the next step
    template = template_env.get_template("template_conf.yml.j2")
    doc_filename = os.path.join(folder_output,
                                conf_paths['result_usage_filename'])
    context = {
        "paths": {
            "resources": __RESOURCES__,
            "jinja": __JINJA__,
            "template": __TEMPLATE__,
            "locale": __LOCALE__,
            "context": __CONTEXT_YML__},
        "version": data['version'],
        "package_name": conf['package_name'],
        "template_parameters": conf['template_parameters'],
    }
    common.set_file_content(doc_filename, template.render(context), bom=False)

    # generate the context for the template
    doc_filename = os.path.join(folder_output, __CONTEXT_YML__)
    config.write_yaml(doc_filename, conf['context'])

###############################################################################
# Generate the template from the conf file
#
# @param conf_filename the filename of the configuration
###############################################################################
def log_chapter(msg):
    logging.info("       __________________________________________      ")
    logging.info("  --==| {:^40} |==--  ".format(msg))
    logging.info("       ¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨      ")

###############################################################################
# Generate the template from the conf file
#
# @param conf_filename the filename of the configuration
###############################################################################
def generate_template_from_conf(conf_template):
    common.check_create_folder(
        conf_template['paths']['template_destination']['root'])
    template_log_handler(conf_template, action_add=True)
    logging.info('+')
    logging.info('-------------------------------------------------------->>')
    log_chapter("Grab resources")
    build_common_resources(conf_template)
    log_chapter("Configure resources")
    configure_resources(conf_template)
    log_chapter("Build the template")
    build_template(conf_template)
    log_chapter("Generate the doc")
    create_doc(conf_template)
    logging.info('<<--------------------------------------------------------')
    logging.info('+')
    template_log_handler(conf_template, action_del=True)

###############################################################################
# Generate the template from the conf file
#
# @param conf_filename the filename of the configuration
###############################################################################
def generate_template(conf_filename):
    """ Generate the template of the main page from a conf file.
    """
    logging.info('+')
    logging.info('-------------------------------------------------------->>')
    logging.info('conf file: %s', conf_filename)
    conf_template = config.read_yaml(conf_filename)
    generate_template_from_conf(conf_template)
    logging.info('<<--------------------------------------------------------')
    logging.info('+')

###############################################################################
# Find the filename of this file (depend on the frozen or not)
# This function return the filename of this script.
# The function is complex for the frozen system
#
# @return the filename of THIS script.
###############################################################################
def __get_this_filename():
    result = ""

    if getattr(sys, 'frozen', False):
        # frozen
        result = sys.executable
    else:
        # unfrozen
        result = __file__

    return result

###############################################################################
# Find the filename of this file (depend on the frozen or not)
# This function return the filename of this script.
# The function is complex for the frozen system
#
# @return the folder of THIS script.
###############################################################################
def __get_this_folder():
    return os.path.split(os.path.abspath(os.path.realpath(
        __get_this_filename())))[0]
