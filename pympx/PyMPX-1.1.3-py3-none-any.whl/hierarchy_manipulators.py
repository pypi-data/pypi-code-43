#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation
'''Empower hierarchy manipulation objects

Hierarchy manipulation is a complex process, and these tools are designed to make that process simpler

Most of the tools are designed to combine two hierarchies to make a third


/****************************************************************************/
/* Metapraxis Limited                                                       */
/* Date: 28-06-2018                                                         */
/*                                                                          */
/*                                                                          */
/* Copyright (c) Metapraxis Limited, 2018.                                  */
/* All Rights Reserved.                                                     */
/****************************************************************************/
/* NOTICE:  All information contained herein is, and remains the property   */
/* of Metapraxis Limited and its suppliers, if any.                         */
/* The intellectual and technical concepts contained herein are proprietary */
/* to Metapraxis Limited and its suppliers and may be covered by UK and     */
/* Foreign Patents, patents in process, and are protected by trade secret   */
/* or copyright law.  Dissemination of this information or reproduction of  */
/* this material is strictly forbidden unless prior written permission is   */
/* obtained from Metapraxis Limited.                                        */
/*                                                                          */
/* This file is subject to the terms and conditions defined in              */
/* file "license.txt", which is part of this source code package.           */
/****************************************************************************/
'''

import sys
import os
import shutil
import fnmatch

import numpy as np
import pandas as pd
#pandas uses constants from the csv module when reading and saving
import csv

import datetime

#Need this for the OrderedDict
import collections

#Need this for zip_longest
import itertools

##Need this to use embedded importer scripts
#import pkg_resources

from pympx import pympx as obmod
from pympx import logconfig
log=logconfig.get_logger()

class TemplateHierarchyBuilder(object):
    ''' It is useful to copy a hierarchy from a template - only certain StructureElements will need rebuilding in the new hierarchy.
    This is very common when building a hierarchy that is being filtered
    
    New Elements will need to be generated to go with the hierarchy, so that appropriate consolidations can be created
    
     
    '''
    def __init__(self
                , template_structure_element
                , previous_version_structure_element
                , build_new_structure_element_rule = None
                , new_name_rule = None
                , template_element_shortcode_field = 'Short Name'
                , template_hierarchy_field=None
                , template_hierarchy_name=None
                , explicit_target_se=None
                ):
        '''Create a new TemplateStructureBuilder
        run the .build() method 
        
        :param template_structure_element: StructureElement (and resulting tree) to be used as a template for the output structure
        :param previous_version_structure_element: StructureElement at root of the previous version of the output structure (if one exists) so that previous versions of elements can be reused 
        :param build_new_structure_element_trigger: A function which takes a structure element and returns True if a replacement one needs to be created. A common example would be a function that determines if any of the children will  
        :param new_name_rule: A function which takes a template StructureElement and returns a new name string (but does not automatically recurse to the children)
        :param hierarchy_field: name of a field which distinguishes elements created for this hierarchy, to enable merges to work successfully
        :param template_element_shortcode_field: name of field in derived elements which links back to the original element shortcode, for allowing comparisons and updates to work correctly
        :param explicit_target_se: Sometimes we know exactly which structure element we wish to build into - e.g. in a nested hierarchy builder
        '''
    
        self.template_structure_element         = template_structure_element
        self.previous_version_structure_element = previous_version_structure_element
        self.output_structure_element           = None
        
        self.build_new_structure_element_rule = build_new_structure_element_rule
        
        self.new_name_rule = new_name_rule
        self.template_element_shortcode_field = template_element_shortcode_field
        
        self.template_hierarchy_field           = template_hierarchy_field
        self.template_hierarchy_name            = template_hierarchy_name
        
        self.explicit_target_se                 = explicit_target_se
        
        #A dictionary for translating the shortcodes of Elements from the template hierarchy to those of the generated hierarchy
        #In the common cases where we have portion of the hierarchy which is a straight copy of the template, we will have a 1:1 shortcode translation, the same on both sides
        self._template_to_new_shortcode_translations = {}
        
        #Record calculations before changing the structure
        #We will be able to see later which calculations have changed
        self.previous_calculation_lookup = {}
        if self.previous_version_structure_element is not None:
            for se in self.previous_version_structure_element.walk():
                self.previous_calculation_lookup[se.shortcode] = se.element.calculation
            
    def build(self):
    
        #First create the Template -> Previous output translations, we will then use these translations to create the output
        #Using the translations prevents us from creating new output Dimension Elements each time we create the newly filtered hierarchy
        #These will be shortname to shortname translations
        # {TEMPLATE:PREVIOUS}
        
        #There are two ways to get these translations - use the 'Template' field (preferred) or use the previous longname 
        #When using the previous longname the order of the walk is important
        #when using the previous longname we set the template field, so that we can use the preferred method next time
        
        #We will need to synchronise elements which have had the template field set
        _elements_for_synchronising = []
        
        _previous_shortcode_exists_lkp = {}
        
        #A dict of longnames to list of elements
        _previous_longname_elements_lkp = {}
        
        
        
        #a dict of template element longnames to tuple of lists of [template] and [previous] elements
        #Seed it with the root elements
        self._template_longname_element_possible_pairings_lkp = {self.template_structure_element.longname : ([self.template_structure_element],[self.previous_version_structure_element.element])}
        
        #first get the translations between template elements and the equivalent target elements
        for el in self.template_structure_element.dimension.elements.values():
            if el.fields[self.template_hierarchy_field] == self.template_hierarchy_name:
                try:
                    template_shortcode = el.fields[self.template_element_shortcode_field]
                    self._template_to_new_shortcode_translations[template_shortcode] = el.shortname
                except KeyError:
                    pass
                
            #At the same time create a simple set of previous version shortcode lookups - so we can see if we have had the same element before, with a simple lookup
            _previous_shortcode_exists_lkp[el.shortname] = True
            
            #At the same time create a longname to [element(s)] lookup
            try:
                _previous_longname_elements_lkp[el.longname].append(el)
            except KeyError:
                _previous_longname_elements_lkp[el.longname]= [el]
        
        #Add explicit target element shortname and longanme to the relevant lookups too        
        if self.explicit_target_se is not None:
            self._template_to_new_shortcode_translations[self.explicit_target_se.shortname] = self.explicit_target_se.shortname
            _previous_shortcode_exists_lkp[self.explicit_target_se.shortname] = True
            
            #At the same time create a longname to [element(s)] lookup
            try:
                _previous_longname_elements_lkp[self.explicit_target_se.longname].append(self.explicit_target_se.element)
            except KeyError:
                _previous_longname_elements_lkp[self.explicit_target_se.longname]= [self.explicit_target_se.element]
         
        #now start building new elements[]
        #We begin by walking and deciding whether a new element needs to be created or reused
        #New elements that need to be created (with the TEMPLATE field) will be created and synchronised
        #After this we'll do a second walk to create the actual structure
        for template_se in self.template_structure_element.walk(permissive = True):
            #Decide whether we should be building a new element from this template, or just copying as is
            if self.explicit_target_se is not None and self.explicit_target_se.shortname == template_se.shortname:
                pass
            elif self.build_new_structure_element_rule(template_se):
                #Check if such an element already exists
                try:
                    target_shortcode = self._template_to_new_shortcode_translations[template_se.shortname]
                    #If we found an element we don't need to create one
                    continue
                except KeyError:
                    #We need to build (or reuse) an element, but no previous element created with the TEMPLATE==shortcode field was found
                    #New we need to see if there was an equivalent element by longname 
                    
                    #Since there may have been multiple elements with the same longname, and some may already have a TEMPLATE field  we need to record possibilities
                    #as lists, not make a decision yet
                    #we will record {current longname : ([structure elements from template hierarchy,...],[possibilities from previous hierarchy,...])}
                    #Since the elements will be recorded in walk order, we can zip them together to get the correct elements each time
                    
                    try:
                        possible_pairings = self._template_longname_element_possible_pairings_lkp[template_se.longname]
                        #Add this template structure element to the list which is the first part of the tuple
                        possible_pairings[0].append(template_se)
                    
                    except KeyError:
                        target_longname = self.new_name_rule(template_se)
                    
                        #Get elements from the previous hierarchy - they may not exist, so do this as a 
                        try:
                            previous_elements = _previous_longname_elements_lkp[target_longname]
                        except KeyError:
                            previous_elements = []
                        
                        #We can't use all of the elememnts, because some of them will already have a template field set
                        #So we will create a new list, of elements we can use
                        previous_elements_we_can_use = []
                        for e in previous_elements:
                            #Check if the element already has a TEMPLATE shortcode - if so it is being used in a different way
                            if e.fields[self.template_element_shortcode_field] is None:
                                previous_elements_we_can_use.append(e)
                        
                        #possible pairings is two lists
                        #The second list is populated once, the first list grows as we walk the template structure
                        possible_pairings = ([template_se],previous_elements_we_can_use)
                        
                        #Now store the tuple in the dictionary. Note, the first element of the tuple will grow
                        self._template_longname_element_possible_pairings_lkp[template_se.longname] = possible_pairings
                
        #Now we have compiled a list of template StructureElements that need to have dimension Elements paired with them (and possibly created)
        #Fill the TEMPLATE shortcode field of elements we pair, and create new elements (and fill the TEMPLATE field) where we don't
        for template_longname, possible_pairings in self._template_longname_element_possible_pairings_lkp.items():
            
            for template_se, previous_el in itertools.zip_longest(possible_pairings[0],possible_pairings[1]):
                
                if previous_el is None:
                    #Create a copy element, and set the template field
                    #Don't copy fields or we will ruin mastering
                    _previous_or_new_element = obmod.Element(shortname = None, longname = self.new_name_rule(template_se),dimension = self.template_structure_element.dimension)
                    
                elif template_se is None:
                    _previous_or_new_element = None                    
                else:
                    #Just set the template field on the previous Element
                    _previous_or_new_element = previous_el
                    
                #Now add the previous Element to the lookup
                #Set the template field on the previous Element
                if _previous_or_new_element is not None:
                    _previous_or_new_element.fields[self.template_element_shortcode_field] = template_se.shortname
                    _previous_or_new_element.fields[self.template_hierarchy_field] = self.template_hierarchy_name
                    #Put the element in - we don't have a shortcode yet
                    self._template_to_new_shortcode_translations[template_se.shortname] = _previous_or_new_element
                    if not _previous_or_new_element.mastered:
                        _elements_for_synchronising.append(_previous_or_new_element)
                    
                #print(template_se.shortcode, previous_se.shortcode)
            #print()
            
        #raise SystemError()
        
        #Merge and synchronise the new or changed Dimension elements
        self.template_structure_element.dimension.elements.merge(_elements_for_synchronising,keys=[self.template_hierarchy_field, self.template_element_shortcode_field] )
        self.template_structure_element.dimension.elements.synchronise()
        
        #print([(el.shortcode,el.longname,el.physid, el.fields[self.template_hierarchy_field], el.fields[self.template_element_shortcode_field]) for el in  _elements_for_synchronising])
        
        #Normalise the translations to just have shortcode:shortcode lookups
        for template_shortcode, output in self._template_to_new_shortcode_translations.items():
            try:
                #print(template_shortcode,'->',output.shortcode,output.longname)
                output_shortcode = output.shortcode
            except AttributeError:
                output_shortcode = output
            
            self._template_to_new_shortcode_translations[template_shortcode] = output_shortcode
            

        #now start building new structure elements
        self.output_structure_element = self._recurse_children(template_se = self.template_structure_element,explicit_target_se = self.explicit_target_se)
            
        return self.output_structure_element
    
        
    def _recurse_children(self,template_se,explicit_target_se=None):
        ''':param explicit_target_se: In some cases we know exactly which target structure element we wish to create'''
        #Decide whether we should be building a new element from this template, or just copying as is
        if explicit_target_se is not None:
            target_element = explicit_target_se.element
        elif self.build_new_structure_element_rule(template_se):
            #Such an element should already have been put into the lookup
            
            target_shortcode = self._template_to_new_shortcode_translations[template_se.shortname]
            if target_shortcode is None:
                target_element = template_se
                self._template_to_new_shortcode_translations[template_se.shortname] = template_se.shortname
                #if template_se.group_only:
                #    target_element = template_se
                #else:    
                #    print(self._template_to_new_shortcode_translations)
                #    raise ValueError('Template element "{}" has no target element'.format(template_se.shortname))
            else:
                target_element = self.template_structure_element.dimension.elements[target_shortcode]
            
        else:
            target_element = template_se.element

        #log.info('263 Creating StructureElement {},{}'.format(template_se.path,repr(template_se ),target_element.shortcode))
        output_se = obmod.StructureElement(element = target_element, structure = template_se.structure)
        try:
            #Filtering specific attribute - does not usually exist
            output_se.filter_in_number = template_se.filter_in_number
        except AttributeError:
            #log.info("Couldn't set filter_in_number from {}".format(repr(template_se)))
            pass
        
        #Now recurse into the template's children
        # += wasn't working, and besides add_child does less work
        for child_se in [self._recurse_children(ch) for ch in template_se.children]:
            #log.info('Adding Child StructureElement {} to {}'.format(child_se.shortcode,output_se.path))
            output_se.add_child(child_se)
        
        return output_se
            
    def compare_template_to_new(self):
        
        return self.template_structure_element.compare(self.output_structure_element
                                                      ,shortcode_translations = {v:k for k,v in self._template_to_new_shortcode_translations.items()})
        
    def compare_previous_to_new(self):
        comp = self.previous_version_structure_element.compare(self.output_structure_element)
        
        comp.add_calculation_comparison(self.previous_calculation_lookup)
        
        return comp
        
    
class FilterHierarchyBuilder(TemplateHierarchyBuilder):
    '''A filter structure builder is a special case of a TemplateStructureBuilder, with post build filtering and consolidation functions inbuilt
    
    
    '''

    #self, template_structure_element, previous_version_structure_element, build_new_structure_element_rule = None, new_name_rule = None, template_element_shortcode_field = 'Short Name'
    def __init__(self
                ,template_structure_element
                ,previous_version_structure_element
                ,filter_in_rule                     = None
                ,shortcode_list                     = None
                ,filter_in                          = None
                ,new_name_rule                      = lambda x: x+ ' excl. filter'
                ,template_element_shortcode_field   = 'Short Name'
                ,consolidate_filtered_elements      = True
                ,post_filter_empty_parents          = True
                ,post_filter_bushify                = True
                ,bushify_additional_rule            = lambda se: True
                ,template_hierarchy_field           = None
                ,template_hierarchy_name            = None
                ,explicit_target_se                 = None
                ):
        '''Create a new FilterHierarchyBuilder
        
        You must run the .build() method in order to actually create the hierarchy
        
        :param template_structure_element: StructureElement (and resulting tree) to be used as a template for the output structure
        :param previous_version_structure_element: StructureElement at root of the previous version of the output structure (if one exists) so that previous versions of elements can be reused 
        :param filter_in_rule: a function that takes a StructureElement and returns True if it is to be kept, False, otherwise
        :param shortcode_list: list of shortcodes to be used to filter the tree, alternative to using a filter rule
        :param filter_in:   True if we wish to include shortcodes in the shortcode_list, False if we wish to exclude them from the tree
        :param new_name_rule: A function which takes a template StructureElement and returns a new name string (but does not automatically recurse to the children)
        :param consolidate_filtered_elements: True if we wish to automatically consolidate elements which have been filtered
        :param template_element_shortcode_field: name of field in derived elements which links back to the original element shortcode, for allowing comparisons and updates to work correctly
        :param post_filter_empty_parents: if empty parents have been created by filtering, filter those out too
        :param post_filter_bushify: After filtering make the tree bushier, less straggly, by putting single children in place of their parents 
        :param explicit_target_se: When we wish to build into a specific target StructureElement, we can inject it via this parameter
        '''
    
        self.filter_in_rule = filter_in_rule
        self.new_name_rule  = new_name_rule
        self.shortcode_list = shortcode_list
        self.filter_in      = filter_in
        
        self.post_filter_empty_parents = post_filter_empty_parents
        self.post_filter_bushify       = post_filter_bushify
        self.bushify_additional_rule   = bushify_additional_rule
        
        self.consolidate_filtered_elements = consolidate_filtered_elements
        
        #Create an equivalent shortcode dictionary to save us using the slow 'in' syntax
        if shortcode_list is None:
            self._shortcode_dict = None
        else:
            self._shortcode_dict = {k:k for k in shortcode_list}
        
        self._template_structure_elements_that_need_to_be_rebuilt = {}
        
        self._element_is_filtered_or_has_filtered_descendants_lookup = {}
        
        self._element_has_completely_filtered_descendants_lookup = {}
        
        #call the base class initialiser
        super().__init__(template_structure_element          = template_structure_element
                         ,previous_version_structure_element = previous_version_structure_element
                         ,build_new_structure_element_rule   = self._build_new_structure_element_rule
                         ,new_name_rule                      = new_name_rule
                         ,template_element_shortcode_field   = template_element_shortcode_field
                         ,template_hierarchy_field           = template_hierarchy_field
                         ,template_hierarchy_name            = template_hierarchy_name 
                         ,explicit_target_se                 = explicit_target_se
                         )
    
    def _filter_out_this_element(self,template_structure_element):
        
        #We never want to filter the root, and it is easy to forget to specify in a structure rule
        if template_structure_element == self.template_structure_element:
            return False
        
        if self.filter_in_rule is not None:
            return not self.filter_in_rule(template_structure_element)
                
        else:
            if self.filter_in:
                #We are implementing a filter in rule
                try:
                    self._shortcode_dict[template_structure_element.shortname]
                    return False
                except KeyError:    
                    #i.e. #if not template_structure_element.shortname in self.shortcode_list: we are filtering it out;
                    return True
            else:
                #We are implementing a filter out rule
                try:
                    #i.e. #if template_structure_element.shortname in self.shortcode_list: we are filtering it out;
                    self._shortcode_dict[template_structure_element.shortname]
                    return True
                except KeyError:    
                    return False
        
        return False
    
    
    
    def _recurse_has_filtered_descendants(self, template_structure_element):
        
        try:
            #Reuse results to save us constantly traversing the tree
            return self._element_is_filtered_or_has_filtered_descendants_lookup[repr(template_structure_element)]
        except KeyError:
            
            result = any(self._recurse_has_filtered_descendants(ch) for ch in template_structure_element.children) or self._filter_out_this_element(template_structure_element)
            #Store the result for reuse
            self._element_is_filtered_or_has_filtered_descendants_lookup[repr(template_structure_element)] = result
        
            return result

    def _recurse_has_completely_filtered_descendants(self, template_structure_element):
        
        try:
            #Reuse results to save us constantly traversing the tree
            return self._element_has_completely_filtered_descendants_lookup[repr(template_structure_element)]
        except KeyError:
            if template_structure_element.is_leaf:
                result = self._filter_out_this_element(template_structure_element)
            else:
                result = all(self._recurse_has_completely_filtered_descendants(ch) for ch in template_structure_element.children) # or self._filter_out_this_element(template_structure_element)
            #Store the result for reuse
            self._element_has_completely_filtered_descendants_lookup[repr(template_structure_element)] = result
        
            return result
              
    
    def _build_new_structure_element_rule(self, template_structure_element):
        
        if self._recurse_has_completely_filtered_descendants(template_structure_element):
            #Do not build a new element if all of the children are filtered
            return False
        else:    
            #build a new element if any one of the descendant elements has been filtered, but this element has not been filtered
            return self._recurse_has_filtered_descendants(template_structure_element) and not self._filter_out_this_element(template_structure_element)
            
    def _post_build_filter_in_rule(self, se):
            #We can't go filtering out the special elements we have just created
            #This rule allows us to adjust the filter rule (which is created referring only to the old hierarchical elements)
            #to apply to the post hierarchy elements
            if se.fields[self.template_hierarchy_field] == self.template_hierarchy_name:
                ##Filter out elements built by the Template Hierarchy builder where we have an explicit element as its parent
                if self.explicit_target_se is not None and se.fields[self.template_hierarchy_field].split('?')[-1] == self.explicit_target_se.shortname:
                    return False
                else:
                    ##Normally we don't Filter out elements built by the Template Hierarchy builder
                    return True
            else:
                return self.filter_in_rule(se)
                        
            
    def build(self):
    
        super().build()
        
        #Gather a list of leaves, so that when post filtering we don't filter the leaves (which naturally have no children of their own)
        if self.post_filter_empty_parents:
            self.prefilter_leaves = list(self.output_structure_element.leaves)
          
        #now filter the build
        self.output_structure_element.filter(filter_rule = self._post_build_filter_in_rule,shortcode_list=self.shortcode_list,filter_in = self.filter_in)
        
        #Now post filter empty parents
        if self.post_filter_empty_parents:
            def post_filter_empty_parent_rule(se):
                if se.is_leaf and se not in self.prefilter_leaves:
                    se.abdicate()
            
            try:
                self.output_structure_element.apply(post_filter_empty_parent_rule)
            except AttributeError:
                #output structure element tried to abdicate self
                # return a list of the children instead 
                return [ch for ch in self.output_structure_element.children.values()]
                    
        #Now prune single child branches back to children, making the tree less straggly
        #e.g.
        #
        # A
        # +-B
        # | +-C
        # +-D
        #   +-E
        #   +-F
        #
        # becomes...
        #
        # A
        # +-C
        # +-D
        #   +-E
        #   +-F
        #
        #eliminating the unnecessary total element B
        if self.post_filter_bushify:
            #print('Bushifying ')
            self.output_structure_element.bushify(bushify_additional_rule=self.bushify_additional_rule)

        if self.consolidate_filtered_elements:
            #Walk the hierarchy
            for se in self.output_structure_element.walk():
                #If the  element has been created for this filtered hierarchy, then consolidate it
                if se.fields[self.template_hierarchy_field] == self.template_hierarchy_name:
                    se.consolidate()
                    se.calculation_status = 'Virtual'
            
        return self.output_structure_element
    
class GraftingHierarchyBuilder(object):
    ''' Combine a rootstock hierarchies with other hierarchies by grafting all the scions on to the leaves of the rootstock
    Unlike the SelectiveGraftingHierarchyBuilder which typically grafts a single scion into parts of a rootstock, this builder grafts each scion element multiple times onto each rootstock leaf
    Because multiple versions of the scion elements will be created, scion elements will be renamed to show that they are a combination of the rootstock
    
    This Hierarchy Builder may create new Dimension Elements.
    '''
    def __init__(self, rootstock_structure_element
                     , scion_structure_elements
                     , previous_version_structure_element = None
                     , new_name_function = lambda lhs, rhs : lhs.longname + ' ' + rhs.longname
                     , element_modification_function = lambda lhs_se,rhs_se,new_se: None
                     , secondary_master_structure_elements = []
                     , key_fields = ['Short Name']
                     , longname_element_lookup = None
                     , allowable_combinations = None
                     , filter_rootstock_leaves_without_children = False
                     ):
        '''Create a new GraftingHierarchyBuilder
        
        You must run the .build() method in order to actually create the hierarchy
        
        :param rootstock_structure_element: StructureElement (and resulting tree) to be used as the rootstock for the output structure
        :param scion_structure_elements: A list of StructureElements (and resulting trees) to be grafted on to every leaf of the 
        :param previous_version_structure_element: StructureElement at root of the previous version of the output structure (if one exists) so that previous versions of elements can be reused 
        :param new_name_function: A function which takes a rootstock StructureElement, and a scion StructureElement and returns a new name string (but does not automatically recurse to the children)
        :param element_modification_function: When creating new elements we will want to set fields so that we can merge correctly. Function will be passed a  A Rootstock Element, and a Scion Element and New StructureElement which can then be modified
        :param secondary_master_structure_elements: When building a hierarchy for the first time we may need to include other hierarchies, to avoid needless elements being created
        
        :param key_fields: A list of element fields which 
        
        :param longname_element_lookup: Dictionary of the form {longname : [Element(), Element(),...]} containing elements that we wish to be considered for re-use. If not given, then a dictionary will be created
        
        :param allowable_combinations: a list of key tuples with keys in the same order as key_fields. If this is None (default) all combinations will be created. If a list then only elements in the list will be included 
        :param filter_rootstock_leaves_without_children: The allowable combinations filter will only work on the generated elements. This flag will filter any rootstock elements that are missing children after the hierarchies have been grafted together
        
        '''
    
        self.rootstock_structure_element        = rootstock_structure_element
        self.scion_structure_elements           = scion_structure_elements
        
        self.previous_version_structure_element = previous_version_structure_element
        self.output_structure_element           = None
        
        self.new_name_function                  = new_name_function
        self.element_modification_function      = element_modification_function
        
        self.secondary_master_structure_elements = secondary_master_structure_elements
        
        self.key_fields                         = key_fields
        
        #We will have an output structure element once the hierarchy is built
        self.output_structure_element           = None
        
        self.dimension = self.rootstock_structure_element.dimension
        
        #Create a longname element lookup if one hasn't been passed in
        if longname_element_lookup is None:
            self.longname_element_lookup = {}
            for e in self.dimension.elements.values():
                #Only use calculated elements in the longname lookup - otherwise we will be shifting real elements around
                #JAT 2018-08-30 15:44
                if e.calculation is not None:
                    try:
                        self.longname_element_lookup[e.longname.replace('"','')].append(e)
                    except KeyError:
                        self.longname_element_lookup[e.longname.replace('"','')] = [e]            
                        
        else:
            self.longname_element_lookup = longname_element_lookup
        
        self.key_element_lookup = {}
        for el in self.dimension.elements.values():
            key_list = []
            for k in self.key_fields:
                found_key = el.fields[k]
                if found_key is None:
                    break
                else:
                    key_list.append(found_key)
                    
            self.key_element_lookup[tuple(key_list)] = el
        
        
        #Turn allowable combinations into a dictionary for lookup speed
        self.allowable_combinations = allowable_combinations
        self.lkp_allowable_combinations = None
        if self.allowable_combinations is not None:
            self.lkp_allowable_combinations = {k:True for k in self.allowable_combinations}
        
        self.filter_rootstock_leaves_without_children = filter_rootstock_leaves_without_children
        
        #Record calculations before changing the structure
        #We will be able to see later which calculations have changed
        self.previous_calculation_lookup = {}
        if previous_version_structure_element is not None:
            for se in self.previous_version_structure_element.walk():
                self.previous_calculation_lookup[se.shortcode] = se.element.calculation
            
    def build(self):
    
        
    
        ### Create new elements
        new_elements=[]
        good_shortname_lkp={}
        self._good_shortname_lkp = good_shortname_lkp
        
        #The leaves of the rootstock will not change shortcode. But each leaf will have a set of scion elements that have changed
        #this dictionary goes {rootstock_leaf_shortcode : {old_scion_shortcode : new_scion_dimension_element, ...}, ...}
        rootstock_leaf_scion_element_translations = {}
        
        self.output_structure_element = self.rootstock_structure_element.copy()
        
        #get_elements is slow - so pre-record as lookups, rather than repeating with every run
        shortname_primary_element_lookup = {}
        shortname_secondary_element_lookup = {}
        
        for se in self.previous_version_structure_element.walk():
            try:
                shortname_primary_element_lookup[se.shortname]
            except KeyError:
                shortname_primary_element_lookup[se.shortname] = se
        for secondary_root in self.secondary_master_structure_elements:
            for se in secondary_root.walk():
                try:
                    shortname_secondary_element_lookup[se.shortname]
                except KeyError:
                    shortname_secondary_element_lookup[se.shortname] = se
                
        
        #go through the leaves of the rootstock
        #take a copy of the leaves now, since they'll be changing with each iteration, and we want what are essentially the copy of the rootstock leaves
        if len(self.output_structure_element.children) == 0:
            output_structure_element_leaves = [self.output_structure_element]
        else:
            output_structure_element_leaves = [l for l in self.output_structure_element.leaves]
        for output_rootstock_leaf in output_structure_element_leaves:
        
            #We will be building new Elements or re-using different elements from the ones in the scion structure
            #These elements will have a 1:1 shortcode translation from old scion to new scion
            old_scion_new_scion_translations = {}
            #this dictionary goes {rootstock_leaf_shortcode : {old_scion_shortcode : new_scion_dimension_element, ...}, ...}
            rootstock_leaf_scion_element_translations[output_rootstock_leaf.shortcode] = old_scion_new_scion_translations
            
            #We will have had a list of root-ish elements to graft on to each leaf            #
            for scion_root in self.scion_structure_elements:
                #Walk through the scion working out whether we need to create new elements
                for scion_el in scion_root.walk():
                
                    #Create the new longname from the rootstock_leaf and scion_element
                    #TODO - when the empower_importer double_quote bug is fixed change this code and the lookup code above
                    new_longname = self.new_name_function(output_rootstock_leaf, scion_el).replace('"','')  
                    
                    #print(sector_leaf.fields['Long Name'],geog_el.fields['Long Name'])
                    new_element_needed = False
                    good_shortname = None
                    
        
                    #Get all of the possible elements with the long name
                    try:
                        elements_with_longname = self.longname_element_lookup[new_longname]
                    except KeyError:
                        elements_with_longname = []

                    primary_element = None
                    secondary_element = None
                    tertiary_element = None

                    provisional_new_element = obmod.Element(shortname = None, longname=new_longname,dimension = self.dimension)
                    #Modify the element - setting fields and the like
                    self.element_modification_function(lhs_se = output_rootstock_leaf.element, rhs_se = scion_el.element, new_se = provisional_new_element)
                    
                    #Now see if any of those elements exist already
                    try:
                        key_lookup_element = self.key_element_lookup[tuple([provisional_new_element.fields[k] for k in self.key_fields])] 
                    except KeyError:
                        key_lookup_element = None
            
                    if key_lookup_element is None:
                        for el in elements_with_longname:

                            try:
                                primary_element = shortname_primary_element_lookup[el.shortname]
                            except KeyError:
                                try:
                                    secondary_element = shortname_secondary_element_lookup[el.shortname]
                                except KeyError:
                                    pass
                                
                            if primary_element is None and secondary_element is None: 
                                tertiary_element_found = True
                                #Compare all of the key fields to see if we have found an element with the key fields we are looking for
                                for key_field in self.key_fields:
                                    tertiary_element_found &= el.fields[key_field] == provisional_new_element.fields[key_field] 
                                if tertiary_element_found:
                                    tertiary_element = el
                    
                    if key_lookup_element is not None:
                        good_shortname_lkp[new_longname] = key_lookup_element
                        self.element_modification_function(lhs_se = output_rootstock_leaf.element, rhs_se = scion_el.element, new_se = key_lookup_element)
                    
                    elif primary_element is not None:
                        #Modify the element - setting fields and the like
                        self.element_modification_function(lhs_se = output_rootstock_leaf.element, rhs_se = scion_el.element, new_se = primary_element.element)
                    
                        good_shortname_lkp[new_longname] = primary_element.element
                    elif secondary_element is not None:
                        #Modify the element - setting fields and the like
                        self.element_modification_function(lhs_se = output_rootstock_leaf.element, rhs_se = scion_el.element, new_se = secondary_element.element)
                        good_shortname_lkp[new_longname] = secondary_element.element
                    #JAT - 2018 08 31 @14:13 - not sure if this section of code will fire off anymore, since we are searching by key in the first instance    
                    elif tertiary_element is not None:
                        #Modify the element - setting fields and the like
                        self.element_modification_function(lhs_se = output_rootstock_leaf.element, rhs_se = scion_el.element, new_se = tertiary_element)
                        good_shortname_lkp[new_longname] = tertiary_element
                    else:
                        good_shortname_lkp[new_longname] = provisional_new_element

                    #print(new_longname)
                    #Once we've chosen the element we want, and modified it with fields, add it to the key_element_lookup, so we can find it next time
                    element = good_shortname_lkp[new_longname]
                    try:
                        self.key_element_lookup[(element.fields[k] for k in self.key_fields)]
                    except KeyError:
                        self.key_element_lookup[(element.fields[k] for k in self.key_fields)] = element
                    
                    
                    if not element.mastered:
                        try:
                            #Check the key fields are populated
                            '~#~'.join([element.fields[f] for f in self.key_fields])
                        except TypeError:    
                            print(element.longname, element.shortcode, [element.fields[f] for f in self.key_fields],repr(element))
                            raise
                        
                        if self.lkp_allowable_combinations is not None:
                            try:
                                self.lkp_allowable_combinations[tuple(element.fields[f] for f in self.key_fields)]
                                create_new_element = True
                            except KeyError:
                                create_new_element = False
                        else:
                            create_new_element = True
                        
                        if create_new_element:                        
                            new_elements.append(element)
                            #Only include in the translation if we have mastered the element or are going to
                            old_scion_new_scion_translations[scion_el.shortcode] = element
                    else:
                        #Only include in the translation if we have mastered the element or are going to
                        old_scion_new_scion_translations[scion_el.shortcode] = element
        
        self.dimension.elements.merge(new_elements, keys = self.key_fields)
        
        self.dimension.elements.synchronise()
        
        ##Put the swap elements in - they seem to get left out of the merge for some reason
        ##This is a bit heavy handed and might slow the whole thing down
        #for output_rootstock_leaf in self.output_structure_element.leaves:
        #
        #    #this dictionary goes {rootstock_leaf_shortcode : {old_scion_shortcode : new_scion_dimension_element, ...}, ...}
        #    old_scion_new_scion_translations = rootstock_leaf_scion_element_translations[output_rootstock_leaf.shortcode] 
        #    
        #    new_translate_elements = []
        #    for el in new_elements:
        #        try:
        #            new_translate_elements.append(old_scion_new_scion_translations[el.shortcode])
        #        except KeyError:
        #            pass
        #    self.dimension.elements.merge(new_translate_elements, keys = self.key_fields)
        #
        #    self.dimension.elements.synchronise()
        
        def _filter_rule(some_element):
            if self.lkp_allowable_combinations is None:
                #print('No lkp_allowable_combinations')
                return True
            else:    
                try:
                    #print(tuple(some_element.fields[f] for f in self.key_fields))
                    self.lkp_allowable_combinations[tuple(some_element.fields[f] for f in self.key_fields)]
                    return True
                except KeyError:
                    return False
            
                
        
        ##Create new structure
        for output_rootstock_leaf in [l for l in self.output_structure_element.leaves]:
        
            #this dictionary goes {rootstock_leaf_shortcode : {old_scion_shortcode : new_scion_dimension_element, ...}, ...}
            old_scion_new_scion_translations = rootstock_leaf_scion_element_translations[output_rootstock_leaf.shortcode] 
                    
            #We will have had a list of root-ish elements to graft on to each leaf            #
            for scion_root in self.scion_structure_elements:
                #print('Scion '+scion_root.shortcode)
                scion_el = scion_root.copy()
                #scion_el.structure = output_rootstock_leaf.structure
                
                if scion_el is not None:
                    
                    #if scion_el.shortname == 'INFINCON' and output_rootstock_leaf.shortname == 'SENEGAL':
                    #    print('INFINCON', 'SENEGAL')
                    #    print(len(scion_el.children))
                    #    for ch in scion_el.children:
                    #        print(ch.shortname)
                    #    scion_el = scion_el.filter(filter_rule = _filter_rule)
                    #    print(scion_el)
                    scion_el = scion_el.swap_elements(shortcode_element_dictionary=old_scion_new_scion_translations)
                    
                    
                    #filter out all child objects that don't exist in our combinations
                    try:
                        scion_el = scion_el.filter(filter_rule = _filter_rule)
                        #print('Post Filter Combo {}'.format(repr(scion_el)))
                
                    except KeyError:
                        print(scion_el.shortname)
                        for ch in scion_el.children:
                            print(ch.shortname)
                        
                        raise
                    
                    #Filter out current object if it is not in the allowed combinations
                    if not _filter_rule(scion_el):
                        scion_el = None
                        #print('Post Filter Combo 2 {}'.format(repr(scion_el)))
                
                    if scion_el is not None: # and len(scion_el.children) > 0 :
                        #Attach the remodelled scion element to the rootstock leaf
                        output_rootstock_leaf.children.append(scion_el)
                        #print('Scion appended {}'.format(repr(scion_el)))
                
            if self.filter_rootstock_leaves_without_children and output_rootstock_leaf.is_leaf:
                #print('Abdicating {}'.format(output_rootstock_leaf.shortcode))
                #print('is_leaf {}'.format(output_rootstock_leaf.is_leaf))
                output_rootstock_leaf.abdicate()
                
        self._rootstock_leaf_scion_element_translations = rootstock_leaf_scion_element_translations
        
        self.output_structure_element.structure = self.previous_version_structure_element.structure
        
        return self.output_structure_element
        
         
    def compare_previous_to_new(self):
        '''Returns an obmod.StructureElementComparison object'''
        comp = self.previous_version_structure_element.compare(self.output_structure_element)
        
        comp.add_calculation_comparison(self.previous_calculation_lookup)
        
        return comp

        
class SelectiveGraftingHierarchyBuilder(object):   
    ''' 
    This Hierarchy Builder takes elements from one hierarchy and slots them into position into another hierarchy, following a rule
    As far as possible, the structure of the scion tree is kept intact
    
    This Hierarchy Builder does not create new Dimension Elements.
    
    '''
    def __init__(self, rootstock_structure_element
                     , scion_structure_element
                     , previous_version_structure_element = None
                     , element_graft_rule = lambda x,y:None
                     , scion_copied_once_only=False
                     , trace_element = None
                     , move_unmapped_leaves_to_root=True
                     ):
        '''Create a new GraftingHierarchyBuilder
        
        When grafting apple trees together, you graft a scion (twig or branch) onto a rootstock tree. This function uses that terminology.
        Create an output hierarchy that takes the rootstock hierarchy and grafts on subtrees from the scion hierarchy.
        Scion StructureElement nodes are grafted on according to a rule which is passed in as a parameter: element_graft_rule.
        An example of an appropriate function to pass in, is one that looks at the underlying fields in the DimensionElements of both hierarchies and decides based on the fields whether a subtree is grafted on to the master tree
        
        You must run the .build() method in order to actually create the hierarchy
        
        :param rootstock_structure_element: StructureElement (and resulting tree) to be used as the rootstock for the output structure
        :param scion_structure_elements: A list of StructureElements (and resulting trees) to be grafted on to every leaf of the 
        :param previous_version_structure_element: StructureElement at root of the previous version of the output structure (if one exists) so that previous versions of elements can be reused 
        
        :param element_graft_rule: Function that takes a rootstock element and scion element and returns True if one should be grafted to the other
        :param scion_copied_once_only: Boolean - does the element merge rule only copy single copies of the scion elements? If so we can optimize by marking nodes as fully transcribed from the scion to the output hierarchy, and avoid visiting them again
        :param return_copy: Boolean - don't graft the scion onto self - rather return a copy of self, with the scion grafted on
        :param trace_element: shortcode or StructureElement. When the grafted tree is coming out with unexpected results you may wish to turn on log tracing for one of the rootstock elements (and its subtree)
        '''
        self.rootstock_structure_element = rootstock_structure_element
        # Copy the structure element so that we can modify it when grafting for optimisation
        self.scion_hierarchy         = scion_structure_element.copy()       
        self.element_graft_rule      = element_graft_rule    
        self.scion_copied_once_only  = scion_copied_once_only
        self.return_copy             = True           
        self.trace_element           = trace_element  
        self.previous_version_structure_element = previous_version_structure_element
        self.move_unmapped_leaves_to_root = move_unmapped_leaves_to_root
        
        #Record calculations before changing the structure
        #We will be able to see later which calculations have changed
        self.previous_calculation_lookup = {}
        if self.previous_version_structure_element is not None:
            for se in self.previous_version_structure_element.walk():
                self.previous_calculation_lookup[se.shortcode] = se.element.calculation
        
    def build(self):
        
        #Note - originally there was a plan to collapse long one dimensional sub-hierarchies in this function. There is no need to do that here - we can tidy up hierarchies in a subsequent step
        
        
        #In a nested loop
        #Walk the rootstock hierarchy
            #Walk the scion hierarchy
                #If the rule says to graft the scion element on then create a copy element and graft it to the output, incrementing the indent if the scion hierarchy requires it
            #After the whole of the scion hierarchy is walked, attach the next element of the rootstock hierarchy to the output hierarchy
        
        scion_hierarchy         = self.scion_hierarchy       
        element_graft_rule      = self.element_graft_rule    
        scion_copied_once_only  = self.scion_copied_once_only
        return_copy             = self.return_copy           
        trace_element           = self.trace_element         
        
        
        copied_scion_structure_elements={}
        
        #Create the root element of the output tree
        current_output_node = None
        #root_output_node = None
        new_rootstock_output_node = None
        previous_rootstock_node = None
        previous_rootstock_level = 0
        
        if trace_element is None:
            trace_element_shortcode = None
        else:
            try:
                #trace_element is a StructureElement or Element
                #ducktyping in action - both have a shortcode
                trace_element_shortcode = trace_element.shortname
            except AttributeError:
                #It didn't quack like a StructureElement or Element so it's a string
                #Add it to another string, just to be sure
                trace_element_shortcode = trace_element + ''
        
            log.info('trace_element_shortcode = {}'.format(trace_element_shortcode))
            
        #Tracing will get turned on by switching the log function
        #Start on debug until we pass the trace element
        trace_log_fn = log.debug
        #tracing_level helps us work out if we have gone far enough up the hierarchy 
        tracing_level = 0 
        tracing_path = None
        
        #Take a copy rather than constantly walking - otherwise the whole process gets very slow
        scion_hierarchy_elements = list(scion_hierarchy.walk(permissive=True))        
        
        #Copy to a list before walking, otherwise the levels change during processing when grafting to self.rootstock_structure_element
        for rootstock_structure_element, rootstock_level in [(e, l) for e, l in self.rootstock_structure_element.walk_with_levels()]:
            
            #Tracing will get turned on by switching the log function
            #Start on debug until we pass the trace element
            if rootstock_structure_element.shortname == trace_element_shortcode:
                trace_log_fn = log.info
                tracing_level = rootstock_level
                
            if rootstock_level is None or rootstock_level < tracing_level:
                #If we have moved back up beyond the tracing level, stop tracing
                trace_log_fn = log.debug
                tracing_level = 0
            
            trace_log_fn('Rootstock walk at {},{}'.format(rootstock_structure_element.shortname,rootstock_level))
            
            if new_rootstock_output_node is not None:
                #Set the current root back to the previous rootstock output node
                current_output_node = new_rootstock_output_node
            
            #if we are returning a copy then we will need a new_rootstock_output_node 
            #if we are grafting on to self.rootstock_structure_element without copying we need to set this new node to self.rootstock_structure_element
            if not return_copy:
                new_rootstock_output_node = rootstock_structure_element
                rootstock_structure_element.set_parent(None)
            else:      
                new_rootstock_output_node = obmod.StructureElement(element = rootstock_structure_element.element)
            
            log.debug('rootstock_level          = '+str(rootstock_level))
            log.debug('previous_rootstock_level = '+str(previous_rootstock_level))
            
            if previous_rootstock_node is not None:
                #log.debug('scion_level     = '+str(scion_level))
                
                if previous_rootstock_level is not None:
                    #Loop back up to the correct parent level 
                    for n in range(1 + previous_rootstock_level-rootstock_level):
                        trace_log_fn('rootstock hierarchy stepping up to previous: ' + str(previous_rootstock_node.shortname))
                        
                        #Parent should never be None if the logic is working
                        if previous_rootstock_node.parent is None:
                            raise SystemError('Moving from level {} to {} at iteration {}. previous_rootstock_node {} has no parent'.format(rootstock_level,previous_rootstock_level,n,previous_rootstock_node.shortname))
                        
                        trace_log_fn('rootstock hierarchy stepping up to parent: ' + str(previous_rootstock_node.parent.shortname))
                
                        previous_rootstock_node = previous_rootstock_node.parent
                
                trace_log_fn('adding new_rootstock_output_node: {} as child to parent previous_rootstock_node: {}'.format(new_rootstock_output_node.shortname,previous_rootstock_node.shortname))
                previous_rootstock_node.add_child(new_rootstock_output_node) 
            else:
                
                root_output_node = new_rootstock_output_node
                
            previous_rootstock_node = new_rootstock_output_node
            previous_rootstock_level = rootstock_level
                    
            current_output_node = new_rootstock_output_node
            trace_log_fn('(Re)Starting scion loop current Rootstock Output Node = '+str(current_output_node.shortname))
            
            n = -1
            
            for scion_structure_element in scion_hierarchy_elements:
                n+=1
                            
                if scion_copied_once_only:
                    try:
                        copied_scion_structure_elements[scion_structure_element.shortname]
                        #walk on to the next scion element
                        continue
                    except KeyError:
                        pass
                
                #Sometimes a Structure Element will appear both in the rootstock and the scion - don't attach to self.rootstock_structure_element
                if current_output_node.element == scion_structure_element.element:
                    trace_log_fn('Counting scion as copied since rootstock and scion elements are equal: {} ({})'.format(current_output_node.element.shortname,n))
                    copied_scion_structure_elements[scion_structure_element.shortname] = scion_structure_element
                    continue
                
                keep_trying_to_graft = element_graft_rule(rootstock_structure_element, scion_structure_element)
                
                while keep_trying_to_graft and current_output_node is not None:
                
                    #Attach the scion if the current output node is the current new_rootstock_output_node - i.e. if we are at rootstock level
                    #Don't link it if it is the same thing - sometimes the rootstock element is also in the scion tree - just use the rootstock version
                    if current_output_node == new_rootstock_output_node:
                        new_scion_output_node = obmod.StructureElement(element = scion_structure_element.element)
                        trace_log_fn('Returned to rootstock. Adding {} ({}) to {} '.format(scion_structure_element.string_to_root,n, current_output_node.shortname))
                        current_output_node.add_child(new_scion_output_node)
                        #record the copied scion element in our dictionary, so that we can shortcut grafting of duplicate elements
                    
                        copied_scion_structure_elements[new_scion_output_node.shortname] = new_scion_output_node
                        
                        current_output_node = new_scion_output_node
                        trace_log_fn('----Scion grafted.  Current Output node set to scion: '+str(current_output_node.shortname)+' ('+str(n)+')')
                        
                        #Set keep_trying_to_graft to False in order to break out of the while loop, which will try to take us back up the hierarchy until we can graft
                        keep_trying_to_graft = False
                        
                    else:
                        #Attach the scion if the current output node was created from an ancestor of the scion_structure_element
                        # THIS IS THE BIT OF MAGIC - that allwos us to retain structure of the scion hierarchy
                        for p in scion_structure_element.ancestors:
                            
                            if p is None:
                                break
                        
                            if p.shortname == current_output_node.shortname:
                                
                                new_scion_output_node = obmod.StructureElement(element = scion_structure_element.element)
                                trace_log_fn('Scion grafting to ancestor of {}. {}({}) added to {}'.format(scion_structure_element.shortname,new_scion_output_node.shortname,n,current_output_node.shortname))
                                current_output_node.add_child(new_scion_output_node)
                                #record the copied scion element in our dictionary, so that we can shortcut grafting of duplicate elements
                                copied_scion_structure_elements[new_scion_output_node.shortname] = new_scion_output_node
                                trace_log_fn('----Current Output node set to '+str(current_output_node.shortname))
                                
                                current_output_node = new_scion_output_node
                                
                                #Set keep_trying_to_graft to False in order to break out of the while loop, which will try to take us back up the hierarchy until we can graft
                                #By breaking out of the while loop we will start trying to graft the next scion node
                                keep_trying_to_graft = False
                                break
                    
                    if keep_trying_to_graft:
                        #If we got this far without grafting, then we couldn't graft the scion node to this current output node
                        #So go up a level, and try to graft there
                        #Eventually we'll meet an ancestor of the current scion, or the new_rootstock_output_node,
                        # and we'll attach to that
                        #trace_log_fn('Bottom of inner loop current Output Node {} moved up to parent. Is now set to {}'.format(current_output_node.parent.shortname, current_output_node.shortname))
                        current_output_node = current_output_node.parent 
                        
        
        if self.move_unmapped_leaves_to_root:
            for leaf in self.scion_hierarchy.leaves:
                #Check if the leaf has been mapped - if not, then put it in the root
                try:
                    copied_scion_structure_elements[leaf.shortname]
                except KeyError:
                    root_output_node.children += leaf.copy()
            
        
        self.root_output_node = root_output_node
        #Return the root node
        return root_output_node        

    def compare_previous_to_new(self):
        comp = self.previous_version_structure_element.compare(self.output_structure_element)
        
        comp.add_calculation_comparison(self.previous_calculation_lookup)
        
        return comp
    
    def build_and_compare(self):
        self.output_structure_element = self.build()
        
        self.comparison = self.compare_previous_to_new()
        
        return self.output_structure_element, self.comparison