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
# standard object to wrap website
# and generate the website
###############################################################################
import logging
import sys
import os
import os.path
import shutil
import copy
import networkx as nx
import jinja2

import pymdtools.common as common
import pymdtools.mdcommon as mdcommon
# import pymdtools.mdcommon as mdcommon
# from pymdtools.mdfile import MarkdownContent
import xe2layout
import xe2layout.config as config

from . import genenv
from . import resource
from . import page
from . import menu
from . import generator

###############################################################################
# Create configuration for the web site generator
#
# @return the conf filename
###############################################################################
def create_conf(filename):
    """ Create a conf file for the website generation.
    @param md_filename the root markdown file
    """
    logging.info("Create website conf for %s", filename)
    filename = common.check_is_file_and_correct_path(filename,
                                                     filename_ext=".md")

    # tpl_conf = common.search_for_file('template_conf.yml',
    #                                   ['./', __get_this_folder()],
    #                                   ['template_generated'], nb_up_path=3)

    context = {
        "md_filename": os.path.split(filename)[1],
        "template_conf_path": "./template/template_conf.yml",
        # os.path.relpath(tpl_conf,
        #                 os.path.split(filename)[0]),
    }

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(__get_this_folder(),
                                                    "templates")),
        autoescape=jinja2.select_autoescape(['html', 'xml']))

    content = template_env.get_template("website_conf.yml.j2").render(context)
    output_filename = common.filename_ext_to(filename, ".yml")

    common.set_file_content(output_filename, content)
    return output_filename


###############################################################################
# Process instruction site:home
###############################################################################
def instruction_home(key, value, site, md_file):
    if key != "home":
        return

    if 'home_key' in site.res.graph:
        logging.warning("home declared for the second time in %s",
                        md_file.relative_filename)

    logging.info("find the home in %s", md_file.full_filename)
    site.res.graph['home_key'] = md_file.relative_filename
    site.res.nodes[md_file.relative_filename]['breadcrumb'] = value


###############################################################################
# Process instruction footer
###############################################################################
def instruction_menu(key, value, site, md_file):
    if key != "menu":
        return
    if 'menu' in site.res.graph:
        logging.warning("menu declared for the second time in %s",
                        md_file.relative_filename)

    general_menu = menu.read_menu(
        md_filename=os.path.join(md_file.filename_path, value),
        base_path=md_file.base_path)
    logging.info("-------------------")
    logging.info(general_menu)
    logging.info("-------------------")
    site.res.graph['menu'] = general_menu

    # add page
    def add_new_page(link):
        if ('url' in link) and (link['url'] not in site.res):
            site.add_page(link['url'])

    general_menu.apply(add_new_page)


###############################################################################
# Process instruction footer
###############################################################################
def instruction_footer(key, value, site, md_file):
    if key != "footer":
        return

    logging.info("find the footer in %s", md_file.full_filename)
    footer_file = os.path.join(md_file.filename_path, value)
    footer_file = common.check_is_file_and_correct_path(footer_file)
    logging.info("footer declared is %s", footer_file)

    if 'footer_links_node' in site.res.graph:
        logging.warning("footer declared for the second time in %s",
                        footer_file)

    footer_content = common.get_file_content(footer_file)
    footer_content = menu.preprocess_menu_add_label(
        footer_content, os.path.split(footer_file)[0])
    links = mdcommon.search_link_in_md_text(footer_content)

    # process link
    for link in links:
        dest_file = os.path.join(os.path.split(footer_file)[0], link['url'])
        target_url = compute_url(site.base_path, dest_file,
                                 source_is_file=False)
        logging.info("Add (for the footer links) the file %s", target_url)
        result_integration = site.add_page(target_url)
        logging.info("     Integration result is %s", result_integration)
        if 'footer_links_node' not in site.res.graph:
            site.res.graph['footer_links_node'] = []

        site.res.graph['footer_links_node'].append(
            {'key': result_integration, 'link': link})


###############################################################################
# Process instruction for saving the data
###############################################################################
def instruction_save_value(key, value, site, _unused_md_file):
    site.res.graph[key] = value

###############################################################################
# get the instruction from name
###############################################################################
@common.static(__inst__=None)
def site_instruction(name):
    if site_instruction.__inst__ is None:
        site_instruction.__inst__ = {}
        site_instruction.__inst__['footer'] = instruction_footer
        site_instruction.__inst__['home'] = instruction_home
        site_instruction.__inst__['menu'] = instruction_menu

    if name not in site_instruction.__inst__:
        return instruction_save_value

    return site_instruction.__inst__[name]

###############################################################################
# Test the key existence
#
# @param graph the graph
# @param key the node key
# @param value the node data to test
# @return the test
###############################################################################
def has_keys(graph, key, value):
    if key not in graph.nodes:
        return False
    return value in graph.nodes[key] and graph.nodes[key][value]


###########################################################################
# compute the url link between two file
#
# @param source the source file or folder
# @param dest the destination file
# @return the url relative
###########################################################################
def compute_url(source, dest, source_is_file=None):
    source_folder = source

    # suppose to be testable
    if (source_is_file is not None and source_is_file) or \
            os.path.isfile(source_folder):
        (source_folder, _unused) = os.path.split(source_folder)

    result = "./" + os.path.relpath(dest, source_folder)
    result = result.replace("\\", "/")
    result = result.replace("//", "/")
    result = result.replace("././", "./")

    return result


###########################################################################
# Add a external link to the graph
#
# @param graph the graph of all nodes
# @param target_url the target url
# @param node_id_source the node_id of the source if possible
# @param initial_link the link for the target
###########################################################################
def add_external_link(resources, target_url,
                      node_id_source=None, initial_link=None):
    is_web_link = False

    if mdcommon.is_external_link(target_url):
        is_web_link = True
        target_url = mdcommon.get_domain_name(target_url)
    else:
        logging.warning('Unidentify resource %s from %s',
                        target_url, repr(node_id_source))
        base_path = resources.graph['base_path']
        if node_id_source is not None:
            base_path = \
                resources.nodes[node_id_source]['resource'].filename_path
        target_url = os.path.join(base_path, target_url)
        target_url = common.set_correct_path(target_url)
        logging.info('Trying to add %s', target_url)

    if target_url not in resources:
        resources.add_node(target_url, is_link=is_web_link)

    if node_id_source is not None:
        resources.add_edge(node_id_source,
                           target_url, links=[initial_link])

    return target_url

###########################################################################
# Find the potential target file form generation info
#
# @param target the target to add to the graph
# @param base_path the root of the path for the target
# @ return the potential target_file
###########################################################################
def target_file(target, base_path):
    if os.path.isfile(target):
        return common.set_correct_path(target)

    return common.set_correct_path(os.path.join(base_path, target))

###########################################################################
# copy all resources to the target and change links
#
# @param resources the graph resources
# @param key the node key
# @param target_folder the folder to copy the resources
# @return the filename of the target
###########################################################################
def create_node_final_resource(resources, key,
                               target_folder, res_target_folder):
    target_folder = common.check_create_folder(target_folder)

    if not has_keys(resources, key, 'is_on_filesystem'):
        return None

    source = resources.nodes[key]['resource']
    dest = resource.Resource(os.path.join(target_folder,
                                          source.relative_filename),
                             target_folder)

    resources_extensions = ['.png', '.jpg']

    if dest.filename_ext == ".md":
        dest.filename_ext = ".html"
    elif dest.filename_ext.lower() in resources_extensions:
        # for other files
        tmp1 = resource.Resource(source.full_filename,
                                 resources.graph['base_path'])
        tmp2 = resource.Resource(target_folder,
                                 resources.graph['dest_root_path'])
        dest = resource.Resource(os.path.join(res_target_folder,
                                              "images",
                                              tmp2.relative_filename,
                                              tmp1.relative_filename),
                                 res_target_folder)

    resources.nodes[key]['target_resource'] = dest
    return dest.full_filename

###############################################################################
# copy all resources to the target and change links
#
# @param resources the graph resources
# @param target_folder the folder to copy the resources
# @return empty
###############################################################################
def create_final_resources(resources, target_folder, res_target_folder):
    target_folder = common.check_create_folder(target_folder)
    for key in resources:
        if has_keys(resources, key, 'is_on_filesystem'):
            create_node_final_resource(resources, key,
                                       target_folder, res_target_folder)


###########################################################################
# adjust links between two file inside the site
#
# @param resources the graph resources
###########################################################################
def adjust_links_url(resources):
    for (src, dest) in resources.edges:
        if has_keys(resources, src, 'is_on_filesystem') and \
                has_keys(resources, dest, 'is_on_filesystem'):
            for link in resources.edges[src, dest]['links']:
                file_src = \
                    resources.nodes[src]['target_resource'].full_filename
                file_dest = \
                    resources.nodes[dest]['target_resource'].full_filename
                link.url = compute_url(file_src, file_dest,
                                       source_is_file=True)


###############################################################################
# Process instruction footer
###############################################################################
def prepare_breadcrumb_links(page_key, resources):
    logging.info("prepare the breadcrumb links for %s", page_key)
    steps = []
    if 'home_key' not in resources.graph:
        return {'steps': steps}

    start_key = resources.graph['home_key']
    page_node_fs = resources.nodes[page_key]['target_resource'].full_filename

    try:
        sh_path = nx.shortest_path(resources, start_key, page_key)
    except nx.NetworkXNoPath:
        sh_path = [start_key, page_key]

    for key in sh_path:
        current_node = resources.nodes[key]
        current_fs = current_node['target_resource'].full_filename
        url = compute_url(page_node_fs, current_fs, source_is_file=True)
        name = current_node['title']
        if 'breadcrumb' in current_node:
            name = current_node['breadcrumb']
        steps.append({"name": name, "url": url})

    steps[-1]['active'] = ""

    return {'steps': steps}


###############################################################################
# Process instruction footer
###############################################################################
def prepare_menu_links(page_key, resources):
    logging.info("prepare the menu links for %s", page_key)
    if 'menu' not in resources.graph:
        return []

    start_menu = copy.deepcopy(resources.graph['menu'])
    page_node_fs = resources.nodes[page_key]['target_resource'].full_filename

    def change_link(link):
        if link.url is None or mdcommon.is_external_link(link.url):
            return
        if link.url not in resources:
            logging.warning("In the general menu, "
                            "the link [%s](%s) leads to nowhere",
                            link.label, link.url)
            return
        link_node = resources.nodes[link.url]
        link_fs = link_node['target_resource'].full_filename
        link.url = compute_url(page_node_fs, link_fs, source_is_file=True)

    start_menu.apply(change_link)

    return start_menu


###############################################################################
# Process instruction footer
###############################################################################
def prepare_footer_links(page_location, resources):
    logging.info("prepare the footer links for %s", page_location)
    result = []
    if 'footer_links_node' not in resources.graph:
        return result
    footer_links_node = resources.graph['footer_links_node']

    for flink in footer_links_node:
        final_link = flink['link']
        # change the url in case of a real file
        if has_keys(resources, flink['key'], 'is_on_filesystem'):
            dest_filename = resources.nodes[flink['key']]['target_resource']
            final_link['url'] = compute_url(page_location,
                                            dest_filename.full_filename,
                                            source_is_file=True)

        result.append(final_link)

    return result

###############################################################################
# An object to rule the web site
###############################################################################
class WebSite:

    ###########################################################################
    # Initialize the object from a content a filename or other
    #
    # @param conf_filename the filename of the yaml parameter for the website
    ###########################################################################
    def __init__(self, websites_conf, website_key):
        logging.debug("Init a website with key %s", website_key)
        if isinstance(websites_conf, str):
            websites_conf = config.read_yaml(websites_conf)

        self.__conf = websites_conf
        self.__conf['current_website_key'] = website_key

        # upload the template
        if 'layout' in self.conf and 'name' in self.conf['layout']:
            if 'version' not in self.conf['layout']:
                self.conf['layout']['version'] = 'latest'

            dest_template = os.path.dirname(
                self.conf['paths']['template_conf'])
            xe2layout.get_release(
                dest_template, self.conf['layout']['name'],
                self.conf['layout']['version'])

        self.__template = genenv.GenerationEnvironment(
            self.conf['paths']['template_conf'])

        self.__resources = nx.DiGraph(
            base_path=self.conf['paths']['root'],
            dest_root_path=self.conf['paths']['destination']['root'])

        if website_key not in self.conf['paths']['entries']:
            logging.warning("The entrie key %s is not defined "
                            "in the website conf", website_key)
            return

        files = self.conf['paths']['entries'][website_key]
        for key in files:
            if os.path.isfile(files[key]):
                self.add_page(files[key])

    ###########################################################################
    # the configuration of the website generation
    # @return the value
    ###########################################################################
    @property
    def conf(self):
        return self.__conf

    ###########################################################################
    # the configuration of the website generation
    # @return the value
    ###########################################################################
    @property
    def website_key(self):
        return self.__conf['current_website_key']

    ###########################################################################
    # the configuration of the website generation
    # @return the value
    ###########################################################################
    @property
    def template(self):
        return self.__template

    ###########################################################################
    # Access to the graph
    # @return the graph
    ###########################################################################
    @property
    def res(self):
        return self.__resources

    ###########################################################################
    # the folder of the first file of the web site the root page
    # @return the value
    ###########################################################################
    @property
    def base_path(self):
        return self.__resources.graph['base_path']

    ###########################################################################
    # Find the potential target file form generation info
    #
    # @param target the target to add to the graph
    # @param base_path the root of the path for the target
    # @param node_id_source the node_id of the source
    # @ return the potential target_fil
    ###########################################################################
    def compute_base_path(self, node_id_source=None):
        if node_id_source is not None:
            return self.res.nodes[node_id_source]['resource'].filename_path

        return self.base_path

    ###########################################################################
    # Add a page node
    #
    # @param md_resource a markdown resource
    ###########################################################################
    def process_directive(self, md_resource):
        if md_resource.filename_ext != ".md":
            return

        the_md = page.Page(md_resource.full_filename)
        data = self.res.nodes[md_resource.relative_filename]
        data['title'] = the_md.md_content.title

        for directive in the_md.site_context:
            site_instruction(directive)(directive,
                                        the_md.site_context[directive],
                                        self, md_resource)

    ###########################################################################
    # Add a page node
    #
    # @param filename the filename of the md file to start
    # @param parent_filename the filename of the md file parent
    ###########################################################################
    def process_md_links(self, md_resource):
        if md_resource.filename_ext != ".md":
            return

        links = mdcommon.search_link_in_md_file(md_resource.full_filename)
        # process link
        for link in links:
            self.add_page(link['url'],
                          node_id_source=md_resource.relative_filename,
                          initial_link=mdcommon.Link(**link))

    ###########################################################################
    # Add a page node
    #
    # @param target the target to add to the graph
    # @param base_path the root of the path for the target
    # @param node_id_source the node_id of the source
    # @param initial_link the text of the link from the source
    ###########################################################################
    def add_page(self, target_url, node_id_source=None, initial_link=None):
        logging.info("Add the resource %s", target_url)

        the_base_path = self.compute_base_path(node_id_source)
        logging.debug("   base_path= %s", the_base_path)

        the_target_file = target_file(target_url, the_base_path)
        logging.debug("   target_file= %s", the_target_file)

        # case if the target is not on the filesystem
        if not os.path.isfile(the_target_file):
            logging.info("    the resource is not a file (external link)")
            return add_external_link(self.res, target_url,
                                     node_id_source=node_id_source,
                                     initial_link=initial_link)

        # case if the target IS ON the filesystem
        the_file = resource.Resource(the_target_file,
                                     base_path=self.base_path)

        if the_file.relative_filename not in self.res:
            is_md = the_file.filename_ext == ".md"
            self.res.add_node(the_file.relative_filename,
                              resource=the_file,
                              is_on_filesystem=True,
                              is_md=is_md)
            if is_md:
                self.process_directive(the_file)
                self.process_md_links(the_file)

        if node_id_source is not None:
            src = node_id_source
            dst = the_file.relative_filename
            if (src, dst) in self.res.edges:
                self.res.edges[src, dst]['links'].append(initial_link)
            else:
                self.res.add_edge(src, dst, links=[initial_link])

        return the_file.relative_filename

    ###########################################################################
    # Add a page node
    #
    # @param filename the filename of the md file to start
    # @param parent_filename the filename of the md file parent
    ###########################################################################
    def generate(self):
        target_folder = \
            self.conf['paths']['destination']['websites'][self.website_key]
        res_target_folder = self.conf['paths']['destination']['resources']

        self.res.graph['root_web_site'] = target_folder

        logging.debug("generate target preprosses")
        create_final_resources(self.res, target_folder, res_target_folder)
        adjust_links_url(self.res)

        logging.info("Copy all resources")
        self.template.resources.copy(res_target_folder)

        for key in self.res:
            logging.info("generate the page %s", key)
            self.create_page(key)

    ###########################################################################
    # Add a page node
    #
    # @param filename the filename of the md file to start
    # @param parent_filename the filename of the md file parent
    ###########################################################################
    def create_page(self, key):
        if not has_keys(self.res, key, 'is_on_filesystem'):
            return None

        source = self.res.nodes[key]['resource']
        dest = self.res.nodes[key]['target_resource']

        if not has_keys(self.res, key, 'is_md'):
            common.check_create_folder(dest.filename_path)
            shutil.copy(source.full_filename,
                        dest.full_filename)
            return

        the_page = page.Page(source.full_filename)

        out_links = []
        for edge in self.res.out_edges(key):
            out_links.extend(self.res.edges[edge]['links'])

        the_page.content = mdcommon.update_links_in_md_text(the_page.content,
                                                            out_links)

        page_produced = generator.generate_page(the_page,
                                                self.template,
                                                self.site_context(key))

        common.check_create_folder(os.path.split(dest.full_filename)[0])
        common.set_file_content(dest.full_filename, page_produced)

    ###########################################################################
    # Add a page node
    #
    # @param filename the filename of the md file to start
    # @param parent_filename the filename of the md file parent
    ###########################################################################
    def site_context(self, key):
        result = copy.deepcopy(self.conf['context']) or {}
        for data in self.res.graph:
            result[data] = self.res.graph[data]

        dest = self.res.nodes[key]['target_resource']
        target_folder = \
            self.conf['paths']['destination']['websites'][self.website_key]
        res_target_folder = self.conf['paths']['destination']['resources']

        if 'home_key' in self.res.graph:
            home_key = self.res.graph['home_key']
            if home_key in self.res.nodes:
                home_node = self.res.nodes[home_key]
                if 'title' in home_node:
                    result['site_title'] = home_node['title']

        result['www_root_path'] = compute_url(dest.full_filename,
                                              target_folder,
                                              source_is_file=True)
        result['res_root_path'] = compute_url(dest.full_filename,
                                              res_target_folder,
                                              source_is_file=True)
        result['footer_links'] = prepare_footer_links(
            dest.full_filename, self.res)

        result['breadcrumb_prepared'] = prepare_breadcrumb_links(key, self.res)

        result['menu_general'] = prepare_menu_links(key, self.res)

        return result

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = ""
        result += "++ Website ---------------------------------------------\n"
        result += "-- Environment -----------------------------------------\n"
        result += str(self.__template)
        result += "-- End Environment -------------------------------------\n"

        result += "-- Graph -----------------------------------------------\n"
        for key in self.__resources.graph:
            result += "%20s=%s\n" % (key, self.__resources.graph[key])
        result += "-- End Graph -------------------------------------------\n"
        result += "++ END Website -----------------------------------------\n"

        return result

###############################################################################
# Create a graph for dot
#
# @return the local folder.
###############################################################################
def generate_site(conf_filename):
    """
    This function build an entire web site.

    @type conf_filename: string
    @param conf_filename: Configuration of the website generation.

    @return nothing
    """
    conf_filename = common.check_is_file_and_correct_path(conf_filename)

    site = WebSite(conf_filename, 'main')
    site.generate()

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
