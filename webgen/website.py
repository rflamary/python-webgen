#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 11:06:43 2012

@author: flam
"""

import configobj, jinja2, sys, argparse, glob
import os, fnmatch, markdown, codecs, shutil
import datetime, imp
import validate
import plugins


# config file specifications
c_file_spec="""
[General]
lang=string(max=3,default='en')
srcdir=string(default='src')
outdir=string(default='out')
templdir=string(default='templates')
plugdir=string(default='plugins')
default_template=string(default='')
default_post_template=string(default='')
default_markup=string(default='markdown')
markdown_extensions=string_list(default=list())
plugins=string_list(default=list())
generate_posts=boolean(default=False)
base_url=string(default='')
[Default]
base_name=string(default='')
base_subname=string(default='')
base_author=string(default='')
[menu]
class_ul=string(default='')
li=string(default='li')
class_li_current=string(default='')
class_li_other=string(default='')
[Links]
class_li_link=string(default='')
[[lists]]
[langbar]
separator=string(default='')
[[__many__]]
text=string(default='')
[copy]
list=list(default=list('robots.txt', '*.css','*.js','images/*'))
"""


default_template="""<!DOCTYPE html>
<html>
<head>
  <title>{{ title }}</title>
</head>
<body>
{{ content }}
</body>
</html>"""

default_config="""
[General]
# langage of pages and posts with no lang info
lang=en

# directories for website source, website output and templates
srcdir='src'
outdir='out'
templdir='templates'
plugdir='plugins'

# default templates (when no template is given in the Salut)
default_template='default'
default_post_template='default'
default_markup='markdown'

#plugins
plugins=menu,copyfile

# generates html for posts
generate_posts=False

[Default]

base_name='Website name'
base_subname='Awesome website'
base_author='me !'

[copy]
list='images/*','*.css','*.js'
"""

default_page="""---
title: empty page
---

# {{ title }}

## Subtitle

empty text
"""

# properties for pages if not set
lst_prop_init=[['reloc',''],
               ['title',''],
               ['sort_info',0],]
               
def to_bool(string):
    """
    crapy str to boolean conversion function to stay compatible with webgen
    """
    if string=='true' or string=='True' or string=='1':
        return True
    else:
        return False
        
def to_list(string):
    """
    convert a str separated by ',' to a list
    """
    return string.split(',')
        
# list of convertion perormed after page loading
lst_prop_convert=[['sort_info',int], ]
                  
def import_(filename):
    """
    import modules as plugins
    """
    (path, name) = os.path.split(filename)
    (name, ext) = os.path.splitext(name)

    (file, filename, data) = imp.find_module(name, [path])
    return imp.load_module(name, file, filename, data)        

def import2_(mod):
    """
    import modules as plugins
    """
    (file, filename, data) = imp.find_module(mod)
    return imp.load_module(name, file, filename, data)  
                  
def init_page_properties(page,plugs=[]):
    """
    Set default page properties values in page dictionnary (to avoid KeyError)
    
    >>> page= dict()
    >>> init_page_properties(page)
    >>> print page
    { 'sort_info': 0, 'reloc': ''}
    """
    for prop in lst_prop_init:
        page[prop[0]]=prop[1]
    for mod in plugs:
        try:
            #print mod.lst_prop_init
            for prop in mod.lst_prop_init:
                page[prop[0]]=prop[1]
        except AttributeError:
            pass

        

def recursiveglob(root,pattern):
    """
    A recursie glob to detect all file in sudirectories whose name fit a pattern
    """
    matches = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches


def load_config(c_file):
    """
    Safe config file loading function
    """
    try:
        config=configobj.ConfigObj(c_file,configspec=c_file_spec.split('\n'), encoding='UTF8')
        
        validator=validate.Validator()
        results = config.validate(validator)

        if results != True:
            for (section_list, key, _) in configobj.flatten_errors(config, results):
                if key is not None:
                    print 'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list))
                else:
                    print 'The following section was missing:%s ' % ', '.join(section_list)
    except configobj.ParseError:
        config=None         
    return config
    
    
def get_page_langage(filename,default='en'):
    """
    get page langage from filename and returns langage and filename without langage
    
    >>> get_page_langage('test.fr.page')
    ('fr', 'test')
    
    >>> get_page_langage('test.page')
    ('en', 'test')
    
    >>> get_page_langage('test.page','fr')
    ('fr', 'test')
    """
    lst=filename.split('.')
    if len(lst)==2:
        lang=default
    else:
        lang=lst[-2]
    return lang,lst[0]
    
    
def get_page_properties(page,raw_file,plugs):
    """
    get page properties from the header of the raw file (list of line)
    
    the format of the header is:
    ---
    prop: prop value
    sort_info: 2
    ---
    The content of the page in raw text is also set in the page dictionnary
    
    """
    #>>> page=dict()
    #>>> raw_file=['---\n','prop: prop value\n','sort_info: 2\n','---\n','\n','text']
    #>>> get_page_properties(page,raw_file)
    #>>> print page
    imax=1
    while not ('---\n' == raw_file[imax]):
        imax+=1
    for i in range(imax-1):
        lst=raw_file[i+1].split(': ')
        if len(lst)>1:
            page[lst[0]]=lst[1][:-1]
        else:
            lst=raw_file[i+1].split(':')
            print('Warning in page {page}:\n\t Property {prop} is not defined properly "name: value" \n\t For empty property use "name: "'.format(prop=lst[0],page=page['srcname']))
    page['raw_text']=''.join(raw_file[imax+1:])
    for prop in lst_prop_convert:
        page[prop[0]]=prop[1](page[prop[0]])    
    for mod in plugs:
        try:
            for prop in mod.lst_prop_convert:
                page[prop[0]]=prop[1](page[prop[0]])
        except AttributeError:
            pass    
    
def get_listdir(path):
    """
    list all sub directories without counting the .svn
    """
    lst=list()
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            tmp=os.path.join(dirname, subdirname)
            if not '.svn' in tmp:
                lst.append(tmp)
    return lst
        
    
class website:
    
    def __init__(self,c_file,verbose=False):
        
        self.verbose=verbose
        
        self.log("Initialization")
        self.config=load_config(c_file)
        
#        self.srcdir=os.path.join(os.getcwd(),self.config['General']['srcdir'])
#        self.outdir=os.path.join(os.getcwd(),self.config['General']['outdir'])
#        self.templdir=os.path.join(os.getcwd(),self.config['General']['templdir'])
        
        self.srcdir=self.config['General']['srcdir']
        self.outdir=self.config['General']['outdir']
        self.templdir=self.config['General']['templdir']
        
        # lists of page ad posts both passed to jinja templates
        self.pagelist=list()
        self.postlist=list()
        
        # list of templates as dictionary
        self.templates=dict()
        
        # list of plugins
        self.plugs=list()      
        
        # dictionnary that will be used in extensions (ext passed to jinja templates)
        self.ext=dict()
        
        # load markdown extensions
        self.md = markdown.Markdown(extensions=self.config['General']['markdown_extensions'])

        # load plugins
        self.log("Loading plugins:")
        self.load_plugins()
        
        # load teh pages
        self.load_website()
        
        #self.get_menus_langbar()
        

    def log(self,txt):
        if self.verbose:
            print(txt)

        
    def load_plugins(self):
        """
        load the plugins listed in config['General']['plugins'] with imp
        """
        for pname in self.config['General']['plugins']:
            self.log("\t" + pname)
            try:
                self.plugs.append(import_(self.config['General']['plugdir']+os.sep+pname))
            except ImportError:
                #try:
                if pname in plugins.plug_list:
                    self.plugs.append(plugins.plug_list[pname])
                else:
                    print("Warning: non-existing plugin '{}'".format(pname))
            
    def apply_plugins(self):
        """
        apply for each plugins the functions:
            - plugin_change_lists(website) that modifies the list of pages and posts
            - plugin_return(config) that returns a plugin info in ext[pluginname] 
            (ext is available in the templates)
        """
        for mod in self.plugs:
            self.log("\t" + mod.__name__)
            self.ext[mod.plug_name]=mod.plugin_return(self.config)
            mod.plugin_change_lists(self)
            

    def apply_plugins_post(self):
        """
        apply for each plugins the functions:
            - plugin_change_lists_post(website) that modifies the website after page generation
            (ext is available in the templates)
        """
        for mod in self.plugs:
            self.log("\t" + mod.__name__)            
            mod.plugin_change_lists_post(self)
        
    def set_links_to_lang(self):
        """
        Convert automatically all the link to the current language if the page is available
        """
        #print page['raw_text']
        for page in self.pagelist:
            s=self.get_langage_str(page['lang'])
            if not s=='':            
                for ptemp in self.pagelist:  
                    #print ptemp['filename_nolang']+'.html'
                    #print ptemp['filename_nolang']+'.'+s+'.html'
                    #print page['raw_text'].find(ptemp['filename_nolang']+'.html')
                    page['raw_text']=page['raw_text'].replace(ptemp['filename_nolang']+'.html',ptemp['filename_nolang']+'.'+s+'.html')
            #print page['raw_text']
            
        for page in self.postlist:
            s=self.get_langage_str(page['lang'])
            if not s=='':            
                for ptemp in self.pagelist:  
                    #print ptemp['filename_nolang']+'.html'
                    #print ptemp['filename_nolang']+'.'+s+'.html'
                    #print page['raw_text'].find(ptemp['filename_nolang']+'.html')
                    page['raw_text']=page['raw_text'].replace(ptemp['filename_nolang']+'.html',ptemp['filename_nolang']+'.'+s+'.html')
        
        
    def get_pages_content(self):
        """
        get content for each page and posts using selected markup
        
        """
        
        #TODO other markup langage (piece of cake)
        for page in self.postlist:
            self.log("\t" + page['filename'])
            temp=self.env.from_string(page['raw_text'])
            page['pre_content']=temp.render(page=page,pagelist=self.pagelist,postlist=self.postlist,postlist_lan=self.postlist_lan,ext=self.ext,**page)
            if page['markup']=='markdown':               
                page['content']=self.md.convert(page['pre_content'])          
        
        
        for page in self.pagelist:      
            self.log("\t" + page['filename'])
            temp=self.env.from_string(page['raw_text'])
            page['pre_content']=temp.render(page=page,pagelist=self.pagelist,postlist=self.postlist,postlist_lan=self.postlist_lan,ext=self.ext,**page)
            if page['markup']=='markdown':               
                page['content']=self.md.convert(page['pre_content'])
        
               

    def sel_post_lan(self):
        """
        select postlist per language 
        """
        
        # list used langages
        langlist=list()
        for page in self.pagelist:
            if not page['lang'] in langlist:
                langlist.append(page['lang'])

        postlist_lan=dict()
        # create list of menus per lang  and per page      
        for lang in langlist:
            postlist_lan[lang]=list()
            # for all posts
            for i in range(len(self.postlist)):
                page=self.postlist[i]
                if page['lang'] == lang:
                    postlist_lan[lang].append(page)
        self.postlist_lan=postlist_lan
        
        
        
    def generate_website(self):
        """
        generate all pages using the corresponding templates.
        
        list of performed tasks:
            - content for each page and post is obtained (using specified markup langage)
            - all pages are written using the selected template
            - if posts are to be generated, then generate them
        """

        # check existing directories in output
        if not os.path.isdir(self.outdir) and self.pagelist:
            os.mkdir(self.outdir)
        for path in self.listdir:
            path=path.replace(self.srcdir,self.outdir)
            if not os.path.isdir(path):
                os.mkdir(path)  

        # apply plugins
        self.log("Apply plugins:")
        self.apply_plugins()
        
        # generate pages content using the selected makup langage
        self.get_pages_content()
        
        # apply plugins after content generation
        self.log("Apply plugins post generation:")
        self.apply_plugins_post()
        
                
        self.log("Write pages:")
        if self.pagelist:
            for page in self.pagelist:
                self.log("\t"+page['filename'])
                #print "Generating page: {page}".format(page=self.outdir+os.sep+page['filename']+'.html')
                
                template=self.templates[page['template']]
                page['raw_page']=template.render(pagelist=self.pagelist,postlist=self.postlist,postlist_lan=self.postlist_lan,ext=self.ext,**page)
                #print page['raw_page']
                f=codecs.open(self.outdir+os.sep+page['filename']+'.html',mode='w', encoding="utf8")
                f.write(page['raw_page'])
                f.close()
    
            if self.config['General']['generate_posts']=='True':
                self.log("Write posts:")
                for page in self.postlist:
                    self.log("\t"+page['filename'])
                    #print "Generating post: {page}".format(page=self.outdir+os.sep+page['filename']+'_post'+'.html')
                    template=self.templates[page['template']]
                    page['raw_page']=template.render(pagelist=self.pagelist,ext=self.ext,postlist=self.postlist,postlist_lan=self.postlist_lan,**page)
                    #print page['raw_page']
                    f=codecs.open(self.outdir+os.sep+page['filename']+'_post'+'.html',mode='w', encoding="utf8")
                    f.write(page['raw_page'])
                    f.close()
        else:
            print('Warning : no pages generated')
        
                        
                

    def get_langage_str(self,lang):
        """
        return eaither an empty string if the langage is the default one or 
        the current lang sting
        """
        if lang==self.config['General']['lang']:
            return ''
        else:
            return lang        
        
    def load_website(self):
        """
        loading the website from the src  folder
        
        several tasks are performed:
            - loading all pages (props in header and raw_text)
            - loading all posst( same)
            - loading all templates in the template folder
            
        """
        
        self.listdir=get_listdir(self.srcdir)
        

        
        self.log("Loading templates:")
        
        # preparing templates (in dictionnary)
        self.env= jinja2.Environment(loader=jinja2.FileSystemLoader(self.templdir))
        self.templates['']=self.env.from_string(default_template)
        for template in recursiveglob(self.templdir,'*.template'):       
            template=template.replace(self.templdir+os.sep,'')
            (head, tail)=os.path.split(template)
            (root, ext)=os.path.splitext(tail)
            self.log("\t"+ root)
            temp=self.env.get_template(template)
            self.templates[root]=temp 
            
            
        # loading pages
        self.log("Loading pages:")
        for page in recursiveglob(self.srcdir,'*.page'):
            temp=dict()
            
            init_page_properties(temp,self.plugs)
            
            # page name extraction
            temp['srcname']=page
            temp['relscrname']=temp['srcname'].replace(self.srcdir+os.sep,'')
            
            (root, ext)=os.path.splitext(temp['relscrname'])
            self.log("\t"+ root)
            temp['filename']=root
            temp['markup']=self.config['General']['default_markup']

            # langage extraction
            temp['lang'],temp['filename_nolang']=get_page_langage(temp['relscrname'],self.config['General']['lang'])  

            temp['template']=self.config['General']['default_template']
            
            # relative position in the website
            nbdir=temp['relscrname'].count('/')
            for i in range(nbdir):
                temp['reloc']+='../'
                
            
            for key in self.config['Default']:
                temp[key]=self.config['Default'][key]
            
            tatbuf = os.stat(page)
            temp['date']=datetime.date.fromtimestamp(tatbuf.st_mtime).isoformat()
            # read page content
            f= codecs.open(page, mode="r", encoding="utf8")
            temp['raw_file']=f.readlines()
            f.close()

            # get properties from file
            get_page_properties(temp,temp['raw_file'],self.plugs)
            
            # test if template exists, if naot, revert
            if not temp['template'] in self.templates:
                print("Warning: template {} not found for page {}, reverting to default".format(temp['template'],page))
                temp['template']=self.config['General']['default_template']
            
            if len(self.get_langage_str(temp['lang'])) and temp['template']+'.'+self.get_langage_str(temp['lang']) in self.templates:
                temp['template']=temp['template']+'.'+self.get_langage_str(temp['lang'])
          
            
            temp['raw_text']=temp['raw_text'].replace('](/','](' +temp['reloc'])
  
            self.pagelist.append(temp)
            
        self.pagelist.sort(key=lambda k: k['sort_info'])
        self.set_links_to_lang()
            
        # loading posts
        self.log("Loading posts:")
        for post in recursiveglob(self.srcdir,'*.post'):

            temp=dict()
            init_page_properties(temp,self.plugs)
            
            # page name extraction
            temp['srcname']=post
            temp['relscrname']=temp['srcname'].replace(self.srcdir+os.sep,'')
            (root, ext)=os.path.splitext(temp['relscrname'])
            self.log("\t"+ root)
            temp['filename']=root
            temp['markup']=self.config['General']['default_markup']

            # langage extraction
            temp['lang'],temp['filename_nolang']=get_page_langage(temp['relscrname'],self.config['General']['lang'])  
            
            temp['template']=self.config['General']['default_template']            

            # relative position in the website
            nbdir=temp['relscrname'].count('/')
            for i in range(nbdir):
                temp['reloc']+='../'
            #temp['reloc']=self.config['General']['base_url']
            

            tatbuf = os.stat(post)
            temp['date']=datetime.date.fromtimestamp(tatbuf.st_mtime).isoformat()
                      
            
            # read page content
            f= codecs.open(post, mode="r", encoding="utf8")
            temp['raw_file']=f.readlines()
            f.close()
            #print temp
            # get properties from file
            get_page_properties(temp,temp['raw_file'],self.plugs)
            
            if len(self.get_langage_str(temp['lang'])) and temp['template']+'.'+self.get_langage_str(temp['lang']) in self.templates:
                temp['template']=temp['template']+'.'+self.get_langage_str(temp['lang'])
            
            # use base_url for forced reloc 
            temp['raw_text']=temp['raw_text'].replace('](/','](' +self.config['General']['base_url'])
            
            self.postlist.append(temp)      
            
        self.postlist.sort(key=lambda k: k['date'],reverse=True)    
        
        self.sel_post_lan()
        
        
def init_default_website():
    try:
        os.mkdir('src')
        os.mkdir('templates')
        
        # default page
        f=open('src/index.page','w')
        f.write(default_page)
        f.close()

        f=open('website.cfg','w')
        f.write(default_config)
        f.close()     
        
        f=open('templates/default.template','w')
        f.write(default_template)
        f.close()       
               
        
    except :
        print("Error: already existing files, use empty folder")




def test():   
   import doctest
   doctest.testmod(verbose=True)

    
    

