 
import codecs
import regex as re
import yaml
import os
import shutil
from warnings import warn
from copy import deepcopy


class Config():
    def __init__(self):
        self.categories = {
            'Part':{'Reuse':False},
            'Tool':{'Reuse':True}
            }
        self.fussy=True
        self.defaultCategory = 'Part'
        self.partLibs = []
        self.debug=False
        self.outDir='Output'
        self.onePage=False
        self.pageBOMTitle = ""

#global config object- I think I am ok with this!
config = Config()

def cleanYAML(txt):
    """
    This function returns a python dictionary from inline YAML.
    It does so by changing all commas into new lines. It also
    does some extra cleanup
    """
    #txt = txt.replace(',','\n')
    # add space after : if forgotten
    
    matches = re.finditer('^(([^:]*?):(\S.*))$',txt,re.MULTILINE)
    for match in matches:
        txt=txt.replace(match.group(1),match.group(2)+': '+match.group(3))
    
    #puts quotes around ? to allow the Qty: ? syntax. This 
    #prohibits complex mapping keys.
    qs = re.findall(':(\s*\?\s*)$',txt,re.MULTILINE)
    for q in qs:
        txt=txt.replace(q," '?'")
    
    pydic = yaml.load(txt.replace(',','\n'), Loader=yaml.SafeLoader)

    return pydic

def replace_ims(text,tofile=True,pageDir=None):
    #Page dir sets directory inside the gitbuilding directory to make relative links work
    
    #Find imageas in the text
    #Group 1: all
    #Group 2: alt-text
    #Group 3: image-path
    #group 4: hover text
    ims = re.findall('(!\[(.*)\]\(\s*(\S+)\s*(?:\"([^\"\n\r]*)\")?\))',text,re.MULTILINE)
    for im in ims:
        imagepath = im[2]
        if (pageDir is not None) and (not os.path.isabs(imagepath)):
            imagepath=os.path.normpath(os.path.join(pageDir,imagepath))
        #The images path relative to the images directory
        imrelpath = os.path.relpath(imagepath,'images')
        if imrelpath.startswith('..'):
            warn(f"Image: {imagepath} is not in the images directory. Image will be coppied into build but may cause unreliable behaviour")
            imrelpath = os.path.split(imagepath)[1]
        #relative to base folder
        newimrelpath = os.path.join('images',imrelpath)
        newimpath = os.path.join(config.outDir,newimrelpath)
        if tofile:
            try:
                if not os.path.exists(os.path.dirname(newimpath)):
                    os.makedirs(os.path.dirname(newimpath))
                shutil.copyfile(imagepath,newimpath)
            except:
                warn(f"Couldn't copy file '{imagepath}' to output, does it exist?")
        #now relative to page
        newimrelpath = os.path.relpath(newimrelpath,pageDir)
        text = text.replace(im[0],f'![{im[1]}]({newimrelpath} "{im[3]}")')
    return text


def replace_stl_links(text,tofile=True,pageDir=None):
    #Find any link to an STL that starts on its own line. Copy STL to output
    
    #Find stls in the text
    #Group 1: all
    #Group 2: link syntax
    #Group 3: stl file
    stls = re.findall('(^(\[[^\]]*\])\((.+?\.stl)\))',text,re.MULTILINE)
    for stl in stls:
        stlpath = stl[2]
        if (pageDir is not None) and (not os.path.isabs(stlpath)):
            stlpath=os.path.normpath(os.path.join(pageDir,stlpath))
        #The stl path relative to the models directory
        stlrelpath = os.path.relpath(stlpath,'models')
        if stlrelpath.startswith('..'):
            warn(f"STL: {stlpath} is not in the models directory. Image will be coppied into build but may cause unreliable behaviour")
            stlrelpath = os.path.split(stlpath)[1]
        #relative to base folder
        newstlrelpath = os.path.join('models',stlrelpath)
        newstlpath = os.path.join(config.outDir,newstlrelpath)
        if tofile:
            try:
                if not os.path.exists(os.path.dirname(newstlpath)):
                    os.makedirs(os.path.dirname(newstlpath))
                shutil.copyfile(stlpath,newstlpath)
            except:
                warn(f"Couldn't copy file '{stlpath}' to output, does it exist?")
        #now relative to page
        newstlrelpath = os.path.relpath(newstlrelpath,pageDir)
        text = text.replace(stl[0],f'{stl[1]}({newstlrelpath})')
    return text

class Documentation(object):
    
    def __init__(self,conf,buildDir=None):
        
        if buildDir is not None:
            assert type(buildDir) is str, 'the build directory must be a string'
            config.outDir = buildDir
            
        confErrMsg = "Error in configuration YAML: "
        
        self.project_data = {'Title': None,'Authors': None,'Email': None,'Affiliation': None,'License': None}
        
        #reading config
        with open(conf, 'r') as stream:
            self.settings = yaml.load(stream, Loader=yaml.SafeLoader)
                    
        
        #All the settings stuff could do with tudying up, it is becoming a lot of repeated code
        
        #Conversion settings
        assert 'OverviewPage' in self.settings, f'{confErrMsg}Cannot run without OverviewPage being set'
        self.overview = self.settings['OverviewPage']
        self.overview_text = None
        if 'CustomCategories' in self.settings:
            assert type(self.settings['CustomCategories']) is dict, f"{confErrMsg}CustomCategories mut be entered as a dictionary"
            #TODO: check all categories have correct reuse info.
            config.categories = {**config.categories, **self.settings['CustomCategories']}
        if 'DefaultCategory' in self.settings:
            assert self.settings['DefaultCategory'] in config.categories, f"{confErrMsg}The default category must be a defined category"
            config.defaultCategory = self.settings['DefaultCategory']
        if 'PartLibs' in self.settings:
            partLibs = self.settings['PartLibs']
            assert type(partLibs) is list, f"{confErrMsg}PartsLibs must be a list not a {type(partLibs)}"
            for lib in partLibs:
                assert type(lib) is str, f"{confErrMsg}Each item in PartsLibs must be a string"
            config.partLibs = partLibs
        if 'Fussy' in self.settings:
            config.fussy = bool(self.settings['Fussy'])
        if 'OnePage' in self.settings:
            config.onePage = bool(self.settings['OnePage'])
        if 'PageBOMTitle' in self.settings:
            config.pageBOMTitle = str(self.settings['PageBOMTitle'])
        else:
            if config.onePage:
                config.pageBOMTitle = "## Bill of materials"
            else:
                config.pageBOMTitle = "## For this step you will need:"
        
        #Project settings
        self.project_data['Homepage'] = self.overview
        self.project_data['OnePage'] = config.onePage
        if 'Title' in self.settings:
            self.project_data['Title'] = self.settings['Title']
            assert type(self.project_data['Title']) is str, f"{confErrMsg}Title must be a string not a {type(self.project_data['Title'])}"
        if 'Authors' in self.settings:
            self.project_data['Authors'] = self.settings['Authors']
            if type(self.project_data['Authors']) is str:
                self.project_data['Authors'] = [self.project_data['Authors']]
            assert type(self.project_data['Authors']) is list, f"{confErrMsg}Authors must be a list not a {type(self.project_data['Authors'])}"
            for author in self.project_data['Authors']:
                assert type(author) is str, f"{confErrMsg}Each author in Authors must be a string"
        if 'Email' in self.settings:
            self.project_data['Email'] = self.settings['Email']
            assert type(self.project_data['Email']) is str, f"{confErrMsg}Email must be a string not a {type(self.project_data['Email'])}"
        if 'Affiliation' in self.settings:
            self.project_data['Affiliation'] = self.settings['Affiliation']
            assert type(self.project_data['Affiliation']) is str, f"{confErrMsg}Affiliation must be a string not a {type(self.project_data['Affiliation'])}"
        if 'License' in self.settings:
            self.project_data['License'] = self.settings['License']
            assert type(self.project_data['License']) is str, f"{confErrMsg}License must be a string not a {type(self.project_data['License'])}"

    def prepare_directory(self,force=False):
        if os.path.isdir(config.outDir):
            curfiles = os.listdir(config.outDir)
            if curfiles != []:
                
                assert os.path.exists(os.path.join(config.outDir,"_data","project.yaml")), "Build directory is not empty, and doesn't appear to be a Git Building output. Empty directory or choose another."
                
                with open(os.path.join(config.outDir,"_data","project.yaml"), 'r') as stream:
                    curproject = yaml.load(stream, Loader=yaml.SafeLoader)
                
                assert 'FileList' in curproject, "This Git Building build directory doesn't have a FileList. Please delete the build directory manually before building"
                
                outfiles = []
                for root, dirs, files in os.walk(config.outDir):
                    for filename in files:
                        if not filename.endswith('project.yaml'):
                            outfiles.append( os.path.relpath(os.path.join(root,filename),start=config.outDir))
                outfiles.sort()
                
                #Unless it is forced the gitbuilding will not delete files in the output directory ready to build, unless they match the files that gitbuilding built last time
                #This way people can't accidentally point gitbuilding at an important directory and delete the contents!
                if not force:
                    assert curproject['FileList'] == outfiles, "Output directory doesn't match the Git Building build. Please delete the build directory manually before building."
            
                for item in os.listdir(config.outDir):
                    itempath = os.path.join(config.outDir,item)
                    if os.path.isdir(itempath):
                        shutil.rmtree(itempath)
                    else:
                        os.remove(itempath)
                    
        else:
            os.mkdir(config.outDir)
        os.mkdir(os.path.join(config.outDir,"images"))
    
    def get_overview_text(self):
        if self.overview_text is None:
            with codecs.open(self.overview, mode="r", encoding="utf-8") as input_file:
                self.overview_text = input_file.read()
        return self.overview_text

    def save_overview_text(self):
        if self.overview_text is not None:
            try:
                with codecs.open(self.overview, mode="w", encoding="utf-8") as input_file:
                    input_file.write(self.overview_text)
                return True
            except:
                return False
        return False
    
    def overview_get_title(self,text):
        match = re.search('^#[ \t]*(\S.*)\n',text,re.MULTILINE)
        if match is not None:
            return match.group(1)
        return None
    
    def build_overview(self,text):
        title = self.overview_get_title(text)
        
        text = replace_ims(text)
        pages = []
        links = re.findall('(\[(.+?)\]\(\s*(\S+)\s*(?:\"(\S+)\")?\s*\))',text,re.MULTILINE)
        for link in links:
            if not link[2].endswith(".md"):
                continue
            
            if not link[2] in pages:
                linkpage = Page(link[2])
                pages.append(linkpage)
            else:
                linkpage = pages[pages.index(link[2])]
            linktext = link[1]
            if linktext == '.':
                linktext = linkpage.title
            newpath = os.path.join(linkpage.filename)
            if link[3] == '':
                alttext=''
            else:
                alttext=f' "{link[3]}"'
            text = text.replace(link[0],f'[{linktext}]({newpath}{alttext})',1)
            
        #Find {{BOMlink}} syntax to replace with link to total Bill of Materials
        BOMlinks = re.findall('(\{\{[ \t]*BOMlink[ \t]*\}\})',text,re.MULTILINE)
        
        for BOMlink in BOMlinks:
            text = text.replace(BOMlink,'[Bill of materials](BOM.md)')
            
        return (text,title,pages)
    
    def buildall(self, force=False):
        #force overrides checking the files in the output folder
        #ONLY USE THIS FOR the server, we don't want people accidentally deleting loads of their files!
        
        
        """
        Overview page is set by config file
        Creates a markdown of this page in the output
        Currently anything linked on this page is also processed
        Eventually this will recursivly go through all links
        This page is treated differently to linked pages, I think
        I am now ok with this!
        """

        self.all_parts = PartList(AggregateList=True)
        
        self.prepare_directory(force)
        
        if not config.onePage:
            text = self.get_overview_text()
            self.overview_processed,title,self.pages = self.build_overview(text)
            
            if title is not None:
                self.project_data['Title'] = title
            else:
                self.project_data['Title'] = "Untitled project"
            
            with codecs.open(os.path.join(config.outDir,self.overview), "w", "utf-8") as outfile:
                outfile.write(self.overview_processed)
                
                
            for lib in config.partLibs:
                self.buildparts(lib)
            
            # count all parts on all pages
            for p in self.pages:
                p.build()
                self.all_parts.merge(p.partlist)

            #Make seperate Bill of materials page
            output=u''
            #predefined all links
            output+= self.all_parts.partlinkmd()
            # Bill of material markdown
            output+= self.all_parts.BOMmd("Bill of Materials")
            
            with codecs.open(os.path.join(config.outDir,"BOM.md"), "w", "utf-8") as outfile:
                outfile.write(output)
        
        else: #onepage
            self.pages = [Page(self.overview)]
            self.pages[0].build()
            self.project_data['Title'] = self.pages[0].title
        
        datadir = os.path.join(config.outDir,"_data")
        if not os.path.isdir(datadir):
            os.mkdir(datadir)
        
        #Add page summary to project data
        self.project_data['PageList'] = []
        for p in self.pages:
            self.project_data['PageList'].append(p.summary())
        
        outfiles = []
        for root, dirs, files in os.walk(config.outDir):
            for file in files:
                outfiles.append(os.path.relpath(os.path.join(root,file), start=config.outDir))
        outfiles.sort()
        self.project_data['FileList'] = outfiles
        
        with open(os.path.join(datadir,"project.yaml"), 'w') as outfile:
            yaml.dump(self.project_data, outfile, default_flow_style=False)
        
        
        

    def buildparts(self,lib):
        """
        This function scans the yaml files of parts and builds a markdown page
        for each of them including information like specs, and supplers
        """
        try:
            with open(f"{lib}.yaml", 'r') as stream:
                partslib = yaml.load(stream, Loader=yaml.SafeLoader)
                
        except:
            warn(f"Not building parts from {lib}.yaml, couldn't read it.")
            return
        libpath = os.path.join(config.outDir,lib)
        if not os.path.isdir(libpath):
            os.mkdir(libpath)
        for key in partslib:
            part = partslib[key]
            key_out = f'# {part["Name"]}\n\n{part["Description"]}\n\n'
            if 'Specs' in part:
                key_out += f'\n\n## Specifications\n\n|Attribute |Value|\n|---|---|\n'
                for skey in part['Specs']:
                    key_out += f'|{skey}|{part["Specs"][skey]:}|\n'
            if 'Suppliers' in part:
                key_out += f'\n\n## Suppliers\n\n|Supplier |Part Number|\n|---|---|\n'
                for skey in part['Suppliers']:
                    key_out += f'|{skey}|[{part["Suppliers"][skey]["PartNo"]}]({part["Suppliers"][skey]["Link"]})|\n'

            with  codecs.open(os.path.join(libpath,f"{key}.md"), "w", "utf-8") as outfile:
                outfile.write(key_out)

class Page(object):
    
    def __init__(self,filepath):
        self.filepath = filepath
        self.filename = os.path.split(filepath)[1]
        self.partlist = PartList()
        
        self.match_sections(self.raw())
        
    def replace_raw(self,md):
        """This is to replace the raw text and rebuild. This is used by the live-editor to update a page."""
        self.clearpartlist()
        self.match_sections(md)
        
    def save(self,md):
        try:
            with codecs.open(self.filepath, "w", "utf-8") as outfile:
                outfile.write(md)
            return True
        except:
            return False
    
    def match_sections(self,text):
        try:
            #Joel probably hates this but string finding is a great time to use regex
            # the brackets () form the three match groups
            # Group 1: searches for any white space character, non-whitespace character, or new line multiple times
            #     the ? makes it not greedy so that group 2 starts ASAP
            # Group 2: searches for a line which begins with a #. then has any number of whitespace characters 0-infinity
            #     then has a non whitespace character, then any non newline character, then a new line
            # Group 3: is inside group 2 and pulls out just the actual title
            # Group 4: is a greedy group that matches everything to the end of the file
            match = re.search('([\s\S\n]*?)(^#[ \t]*(\S.*)\n)([\s\S\n]*)',text,re.MULTILINE)

            self.preamble = match.group(1)
            self.header = match.group(2)
            self.title = match.group(3)
            self.maintext = match.group(4)
        except:
            self.preamble = ''
            self.header = ''
            self.title = ''
            self.maintext = text
        
    def __eq__(self,other):
        return self.filepath == other
    
    def raw(self):
        try:
            with codecs.open(self.filepath, mode="r", encoding="utf-8") as input_file:
                text = input_file.read()
        except:
            warn(f"Failed to load a page from {filepath}")
            raise
        return text
    
    def clearpartlist(self):
        self.partlist = PartList()
    
    def summary(self):
        return {'Title': self.title,'Link': self.filepath}
    
    def scanpreamble(self):
        #Regex of preamble looks for links for page part definitions
        #Group 1: part name
        #Group 2: link location
        #Group 3: YAML syntax for description
        part_descriptions = re.findall('^[ \t]*\[(.+)\]:[ \t]*(\S*)(?:[ \t]+"([\s\S]*?)")?',self.preamble,re.MULTILINE)
        
        #Populate the part dictionary
        for description in part_descriptions:
            # Create part object of the description and append it to the part list for each part defined in the preamble
            self.partlist.append(Part(description))
        
    def build(self,tofile=True):
        #tofile is set to false if you dont want the builds to be produced (this is used in the live preview)
        
        self.scanpreamble()
        
        #Find each part reference in main text. This is a link followed by {some YAML}
        part_refs = re.findall('(\[([^\]]+?)\](?:\((.*?)\))?\{(.*?)\})',self.maintext,re.MULTILINE)
        

        # Loop through each part ref
        for part_ref in part_refs:
            try:
                self.partlist.countpart(part_ref[1:])
                #Remove full link text and replace with reference style link
                self.maintext = self.maintext.replace(part_ref[0],f'[{part_ref[1]}]')
            except:
                warn(f'Broken part reference:\n{part_ref[0]}\nneeds fixing.')
                    
        # Once part refs all scanned, if Qty for page was undefined initially set to quantity used.
        self.partlist.finishcounting()
        
        if config.debug:
            print(f"\n\n***** PAGE: {self.title}*****\n")
            for part in self.partlist:
                print(part)
        
        self.maintext = replace_ims(self.maintext,tofile=tofile)
        
        #Find {{BOM}} syntax to replace with bill of materials text
        BOMs = re.findall('(\{\{[ \t]*BOM[ \t]*\}\})',self.maintext,re.MULTILINE)
        
        #If bill of material is needed for this page, generate the markdown for it
        if len(BOMs)>0:
            BOM=True
        else:
            BOM=False
        
        if BOM == True:
            BOMtext = self.partlist.BOMmd(config.pageBOMTitle)
        
        #Place bill of materials into page
        for bom in BOMs:
            self.maintext = self.maintext.replace(bom,BOMtext)
        
        #copy linked markdown pages to output
        for linkedPage in self.partlist.links():
            if os.path.exists(linkedPage):
                if linkedPage.endswith('.md') or linkedPage.endswith('.stl'):
                    relpath = os.path.relpath(linkedPage)
                    lpdir,lpname = os.path.split(relpath)
                    if lpdir.startswith('..'):
                        warn('Included files should be in the project directory')
                    lpoutdir = os.path.join(config.outDir,lpdir)
                    if not os.path.exists(lpoutdir):
                        os.makedirs(lpoutdir)
                    outpath = os.path.join(lpoutdir,lpname)
                    if linkedPage.endswith('.stl'):
                        shutil.copyfile(linkedPage,outpath)
                        with codecs.open(outpath[:-3]+'md', "w", "utf-8") as outfile:
                            output = u''
                            output += f'# {lpname[:-4]}\n\n'
                            output += f'[Download STL]({lpname})\n\n'
                            outfile.write(output)
                    else: #markdown part file
                        with codecs.open(linkedPage, mode="r", encoding="utf-8") as linked_file:
                            part_md = linked_file.read()
                        part_md = replace_ims(part_md,pageDir=lpdir)
                        part_md = replace_stl_links(part_md,pageDir=lpdir)
                        with codecs.open(outpath, "w", "utf-8") as outfile:
                            outfile.write(part_md)
        
        
                        
        
        #Write output
        output = u''
        
        #Predefine all part links
        output+= self.partlist.partlinkmd()
        
        #Title and text
        output += f'\n\n# {self.title}\n\n'

        output+=self.maintext.lstrip()
        
        if tofile:
            #Write to file in Output folder
            with codecs.open(os.path.join(config.outDir,self.filename), "w", "utf-8") as outfile:
                outfile.write(output)
            return None
        else:
            return output



class Part():
    
    def __init__(self,info,indexed=True):
        
        self.name = info[0]
        partlink = info[1]
        partyaml=info[2]
        
        if not partyaml is '':
            part_info = cleanYAML(partyaml)
        else:
            part_info = dict()
        
        #set Part defaults
        self.link=None
        self.cat=config.defaultCategory
        self.cat_assumed = True
        self.reuse=False
        #None for total quantity would mean that no total is defined and it is calculated from number used
        self.total_qty=None
        #qty_used is set as None because type has not yet been set
        self.qty_used=None
        # An indexed part is one that has been added to a partlist
        self.indexed = indexed
        
        #Set link
        if not partlink == '':
            partlink = os.path.normpath(partlink)
            if not os.path.isabs(partlink):
                if partlink.startswith('..'):
                    warn(f'Link to "{partlink}" removed as path must be within documentation dir')
                else:
                    self.link = partlink
            else:
                warn(f'Link to "{partlink}" removed as only relative paths are supported')
            
        handlecategoryshorthand(part_info)
        
        if 'Cat' in part_info:
            self.cat=part_info['Cat']
            self.cat_assumed = False
            try:
                self.reuse = config.categories[self.cat]['Reuse']
            except KeyError:
                warn(f"No valid category {part['Cat']}. Assuming no part reuse, you can define custom categories in the config file.")
                
        
        #interpret YAML differently if the part is added as a predefined part in the preamble or added on the fly in the text
        if indexed:
            # if Qty not defined or set as ?, leave qty as None
            if 'Qty' in part_info:
                if part_info['Qty']!='?':
                    self.total_qty = part_info['Qty']
        else:
            if 'Qty' in part_info:
                self.qty_used=part_info['Qty']
            if 'TotalQty' in part_info:
                self.total_qty = part_info['TotalQty']
    
    def __eq__(self,obj):
        assert type(obj) is Part, 'Can only compare a Part to another Part'
        # Check type depends on if an indexed part (one in a PartList) is compared to another indexed part or one not yet indexed (see below)
        checkType = self.indexed+obj.indexed
        assert checkType == 1 or checkType == 2, "Part comparison failed, are you trying to compare two non-indexed Parts?"
        
        
        if checkType == 1:
            #Non indexed part compared to an indexed one.
            #This will be for checking whether to increment the parts used or to index the part as a new part
            #Categories don't need to match here as using "Qty" for a part to be counted shouldn't set the category
            
            if self.name != obj.name:
                # names must match
                return False
            
            if self.link == obj.link:
                # categories, names and links match
                return True
            
            if obj.link is None or self.link is None:
                    return True
            
            warn(f"Parts on same page have the same name {obj.name} and different links [{self.link},{obj.link}. "+
                 "This may cause weird Bill of Materials issues. Define link in preamble to avoid.")
            return False
        
        else:
            #comparing two parts already in parts lists on different pages.
            
            # categories must match
            if self.cat != obj.cat:
                # names must match
                return False
            
            if (self.link is not None) and (obj.link is not None):
                # If links match then they are reffering to the same part
                if self.link == obj.link:
                    if (self.name != obj.name) and config.fussy:
                        warn(f"Fussy warning: Parts on different pages have same name {obj.link} and different names "+
                                "[{self.name},{obj.name}. One name will be picked for the total Bill of Materials. Define "+
                                "link in preamble to avoid, you can ignore fussy warnings by editing your config")
                    return True
                else:
                    return False
            else:
                #if either link is None check name
                if self.name == obj.name:
                    #items with the same name is a match if at least one link is None
                    return True
                
    def __str__(self):
        return f'''{self.name:}
    link:      {self.link}
    category:  {self.cat}
    reuse:     {self.reuse}
    Total Qty: {self.total_qty}
    Qty Used:  {self.qty_used}
    '''
    
    def combine(self,part):
        #combine is different from counting, combine is the operation when two lists are merged
        # as such all parts should be indexed
        assert type(part) is Part, "Can only add a Part to a Part"
        self.indexed, "Part must be indexed to be added to"
        part.indexed, "Can only add indexed parts"
        assert part==self, "Parts must match to be added"
        
        #Some quantities used might be None
        if self.qty_used is not None and part.qty_used is not None:
            #Neither are none
            try:
                # make part have same data type for quantity
                part.qty_used = type(self.qty_used)(part.qty_used)
            except ValueError:
                warn(f"Cannot add/compare {self.qty_used} and {part.qty_used} for Part: {part.name}")
            if self.reuse: 
                self.qty_used = max( self.qty_used, part.qty_used )
            else:
                self.qty_used += part.qty_used
        elif self.qty_used is None and part.qty_used is not None:
            #Currently none but input is not none
            self.qty_used = part.qty_used
        #Other cases where input is none no change is needed
        
        #Totals should have been cunted so there should be no nones!
        try:
            # make part have same data type for quantity   
            part.total_qty = type(self.total_qty)(part.total_qty)
        except ValueError:
            warn(f"Cannot add/compare {self.total_qty} and {part.total_qty} for Part: {part.name}")
        
        if self.reuse: 
            self.total_qty = max( self.total_qty, part.total_qty )
        else:
            self.total_qty += part.total_qty

            
        
    def count(self,part):
        assert self.indexed, "Only indexed parts can count parts other parts"
        assert not part.indexed, "Can only count non indexed parts"
        
        if not self.cat == part.cat:
            if part.cat_assumed:
                pass
            elif self.cat_assumed:
                self.cat = part.cat
                #if no parts have been used and the category initally set was assumed
                #then there are no problems
                if not self.qty_used == None:
                    warn(f"Warning: Category of {self.name} is set after first use. This could cause a counting error!")
            else:
                warn(f"Warning: Confilcting categories explicitly set. For {self.name}")
        
        if self.qty_used == None:
                self.qty_used = part.qty_used
        else:
            
            try:
                # make part have same data type for quantity
                part.qty_used = type(self.qty_used)(part.qty_used)
            except ValueError:
                warn(f"Cannot add/compare {self.qty_used} and {part.qty_used} for Part: {part.name}")
            
            if self.reuse: 
                self.qty_used = max( self.qty_used, part.qty_used )
            else:
                self.qty_used += part.qty_used
                                

class PartList():
    
    def __init__(self,AggregateList=False):
        #aggregate lists are summed lists, a non agregate list cannot become and agregate
        self.aggregate = AggregateList
        #All agregate lists are counted, normal lists should be counted before merging into aggregates or calculating a bill of materials
        self.counted = AggregateList
        self.parts=[]
    
    def __getitem__(self,ind):
        return self.parts[ind]
    
    def __setitem__(self,ind,part):
        assert type(part) is Part, "Can only store Part objects in a PartList"
        self.parts[ind] = part
    
    def __len__(self):
        return len(self.parts)

    def append(self,part):
        assert type(part) is Part, "Can only append Part objects to a PartList"
        #TODO: Check if parts clash
        self.parts.append(deepcopy(part))
        
    def merge(self,inputlist):
        assert type(inputlist) is PartList, "Can only merge a PartList to another PartList"
        assert self.aggregate, "Only aggregate lists can merge other lists into them"
        assert inputlist.counted, "List must be counted before being merged into an aggregate"
        for part in inputlist:
            if part in self:
                ind = self.parts.index(part)
                self[ind].combine(part)
            else:
                self.append(part)
        
    def countpart(self,info):
        assert not self.counted, "Cannot count part, counting has finished"
        part = Part(info,indexed=False)
        
        # if the part is already listed, update quantites
        if part in self.parts:
            ind = self.parts.index(part)
            self[ind].count(part)
        else:
            part.indexed=True
            self.append(part)
    
    def finishcounting(self):
        if self.counted:
            return None
        #once counting is finished, if the total quantity was undefined set it to the quantity used
        for part in self.parts:
            if part.total_qty is None:
                part.total_qty = part.qty_used
        self.counted=True
        
    def partlinkmd(self):
        linktext = u''
        for part in self.parts:
            if part.link is None:
                link = 'missing'
            elif part.link.endswith('.stl'):
                link = part.link[:-3]+'md'
            else:
                link = part.link
            linktext+=f'[{part.name}]:{link}\n'
        return linktext
    
    def links(self):
        links = []
        for part in self.parts:
            if part.link is not None:
                links.append(part.link)
        return links
        
    def BOMmd(self,title,divide=True):
        assert self.counted, "Cannot calculate bill of materials for uncounted partlist."
        BOMtext=f'{title}\n\n'
        # Loop through parts and put quantities and names in/
        for cat in config.categories:
            first = True
            for part in self.parts:
                if part.cat == cat:
                    if first:
                        first=False
                        BOMtext+=f'### {cat}s\n\n'
                    if part.total_qty is None:
                        qty_str = 'Some '
                    elif type(part.total_qty) is int:
                        qty_str = str(part.total_qty)+' x '
                    elif type(part.total_qty) is float:
                        qty_str = str(part.total_qty)+' of '
                    else:
                        qty_str = str(part.total_qty)
                    # If quantity for the page was set to a different number to the quantity used. Both are displayed
                    if part.total_qty==part.qty_used:
                        used_txt = ''
                    else:
                        used_txt= f'  (Used: {part.qty_used} )'
                    BOMtext+=f'* {qty_str} [{part.name}]{used_txt}\n'
        return BOMtext

def handlecategoryshorthand(part):
    for key in config.categories:
        if key in part:
            part['Qty']=part[key]
            part['Cat']=key
            del part[key]
            return None

