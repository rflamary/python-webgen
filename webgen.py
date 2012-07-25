#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 11:06:43 2012

@author: flam
"""

import configobj, jinja2, sys, argparse, glob
import os, fnmatch, markdown, codecs, shutil
import datetime

c_file='config.cfg'

# config file specifications
c_file_spec="""
[General]
lang=string(max=2,default='en')
srcdir=string(default='src')
outdir=string(default='out')
templdir=string(default='templates')
default_template=string(default='default')
default_post_template=string(default='default')
default_markup=string(default='markdown')
generate_sitemap=boolean(default=True)
base_url=string(default='')
base_name=string(default='')
base_subname=string(default='')
base_author=string(default='')
generate_posts=boolean(default=False)
[Menu]
class_li_current=string(default='')
class_li_other=string(default='')
[Links]
class_li_link=string(default='')
[[lists]]
[LangBar]
uselangbar=boolean(default=True)
separator=string(default='')
[[__many__]]
text=string(default='')
[Pattern]
[[Copy]]
list=list(default=list('robots.txt', '*.css','*.js','images/*'))
"""

# properties for pages if not set
lst_prop_init=[['langbar',''],
               ['menu',''],
               ['reloc',''],
               ['sort_info',0],
               ['in_menu','false'],
               ['sitemap_priority',.5],
               ['sitemap_frequency','weekly']]

# list of convertion perormed after page loading
lst_prop_convert=[['sort_info',int],
                  ['sitemap_priority',float]]
                  
def init_page_properties(page):
    """
    Set default page properties values in page dictionnary (to avoid KeyError)
    
    >>> page= dict()
    >>> init_page_properties(page)
    >>> print page
    {'menu': '', 'in_menu': 'false', 'sitemap_priority': 0.5, 'sitemap_frequency': 'weekly', 'sort_info': 0, 'langbar': '', 'reloc': ''}
    """
    for prop in lst_prop_init:
        page[prop[0]]=prop[1]

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
        config=configobj.ConfigObj(c_file,configspec=c_file_spec.split('\n'))
    except configobj.ParseError:
        config=None         
    return config
    
    
def get_page_langage(filename,default='en'):
    """
    get page langage from filename and returns langage and filename without langage
    
    truc plus long
    
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
    
def find_page(filename,lst):
    """
    check if a page exist in a list of pages (dict)
    
    >>> lst=[dict(filename='file'+str(i)) for i in range(10) ]
    >>> find_page('file3',lst)
    True
    >>> find_page('test',lst)
    False
    """
    found=False
    for page in lst:
        if page['filename']==filename:
            found=True
    return found
    
def get_sitemap_url(loc,changefreq='weekly',lastmod='',priority=.5):
    """
    returns the string for a given url in a sitemap
    
    >>> print get_sitemap_url('test'),
    <url>
    <loc>test</loc>
    <changefreq>weekly</changefreq>
    </url>
    """
    res=u'<url>\n'
    res+=u'<loc>{0}</loc>\n'.format(loc)
    res+=u'<changefreq>{0}</changefreq>\n'.format(changefreq)
    if not lastmod=='':
        res+=u'<lastmod>{0}</lastmod>\n'.format(lastmod)
    if not priority==.5:
        res+=u'<priority>{0}</priority>\n'.format(priority)        
    res+=u'</url>\n'
    return res
    
    
def get_page_properties(page,raw_file):
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
        page[lst[0]]=lst[1][:-1]
    page['raw_text']=''.join(raw_file[imax+1:])
    for prop in lst_prop_convert:
        page[prop[0]]=prop[1](page[prop[0]])    
    
    
def get_listdir(path):
    lst=list()
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            tmp=os.path.join(dirname, subdirname)
            if not '.svn' in tmp:
                lst.append(tmp)
    return lst
        
    
class website:
    
    def __init__(self,c_file):
        
        self.config=load_config(c_file)
        
        self.srcdir=os.path.join(os.getcwd(),self.config['General']['srcdir'])
        self.outdir=os.path.join(os.getcwd(),self.config['General']['outdir'])
        self.templdir=os.path.join(os.getcwd(),self.config['General']['templdir'])
        
        self.srcdir=self.config['General']['srcdir']
        self.outdir=self.config['General']['outdir']
        
        # lists of page ad posts both passed to jinja templates
        self.pagelist=list()
        self.postlist=list()
        
        self.templates=dict()
        
        # dictionnary that will be used in extensions (ext passed to jinja templates)
        self.ext=dict()
        
        self.md = markdown.Markdown()
        
        self.load_website()
        
        self.get_menus_langbar()
        
    def set_links_to_lang(self):
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

        
        
    def get_pages_content(self):
        """
        get content for each page and posts using slected markup
        
        """
        
        #TODO other markup langage (piece of cake)
        
        for page in self.pagelist:            
            if page['markup']=='markdown':               
                page['content']=self.md.convert(page['raw_text'])
        
        for page in self.postlist:            
            if page['markup']=='markdown':               
                page['content']=self.md.convert(page['raw_text'])  
                
    def get_menus_langbar(self):
        """
        add the 'menu' and 'langbar' key containt html list to all pages 
        """
        
        # list used langages
        langlist=list()
        for page in self.pagelist:
            if not page['lang'] in langlist:
                langlist.append(page['lang'])
                
        self.langlist=langlist


        postlist_lan=dict()
        # create list of menus per lang  and per page      
        for lang in langlist:
            postlist_lan[lang]=list()
            menulist=list()
            for i in range(len(self.pagelist)):
                page=self.pagelist[i]
                if page['lang']== lang and page['in_menu'] == 'true' :
                    menulist.append(i)
            # for all pages
            for i in range(len(self.pagelist)):
                page=self.pagelist[i]
                if page['lang'] == lang:
                    page['menu']=self.get_menu(menulist,i) 
                    page['langbar']=self.get_langbar(i)
            # for all posts
            for i in range(len(self.postlist)):
                page=self.postlist[i]
                if page['lang'] == lang:
                    page['menu']=self.get_menu_post(menulist,i)                    
                    page['langbar']=self.get_langbar_post(i)
                    postlist_lan[lang].append(page)
        self.postlist_lan=postlist_lan
        
                    
    def get_menu(self,menulist,i):
        """
        get html menu with pages selected in menulist for page i (index).
        the selected page is not a link and has a different il class
        """
        res="<ul>\n"
        rel=self.pagelist[i]['reloc']
        for j in menulist:
            page=self.pagelist[j]
            if j==i:
                res+=u'\t\t<li class="{classe}"><span>{title}</span></li>\n'.format(classe=self.config['Menu']['class_li_current'],title=page['title'])
            else:
                res+=u'\t\t<li class="{classe}"><a href="{adress}.html">{title}</a></li>'.format(classe=self.config['Menu']['class_li_other'],title=page['title'],adress=rel+page['filename'])
        res+="</ul>\n"
        return res
        
    def get_links(self):
        """
        get html list of links to be included in the pages
        """
        res="<ul>\n"
        for lnk in self.config['Links']['list']:
            res+=u'\t\t<li class="{classe}"><a href="{url}" title="{txt}">{txt}</a></li>\n'.format(classe=self.config['Links']['class_li_link'],txt=lnk,url=self.config['Links']['list'][lnk])
        res+="</ul>\n"        
        return res
        
    def get_menu_post(self,menulist,i):
        """
        get html menu with pages selected in menulist for post i (index)
        no pages are select in this case
        """        
        res="<ul>\n"
        rel=self.postlist[i]['reloc']
        for j in menulist:
            page=self.pagelist[j]
            res+=u'\t\t<li class="{classe}"><a href="{adress}.html">{title}</a></li>'.format(classe=self.config['Menu']['class_li_other'],title=page['title'],adress=rel+page['filename'])
        res+="</ul>\n"
        return res
        
    def get_langbar(self,i):
        """
        get the html for the langbar of page i (using reloc to always point well)
        """
        res=''
        page=self.pagelist[i]
        for lang in self.langlist:
            if len(self.get_langage_str(lang)):
                adress=page['filename_nolang']+'.'+self.get_langage_str(lang)
            else:
                adress=page['filename_nolang']
            if find_page(adress,self.pagelist):
                text=self.config['LangBar'][lang]['text'].format(reloc=page['reloc'])
                #print '{0}'.format(self.config['LangBar'][lang]['text'])
                res+=u'<a href="{adress}.html">{text}</a>{sep}'.format(adress=page['reloc']+unicode(adress),text=unicode(text),sep=unicode(self.config['LangBar']['separator']))
        return res
            
    def get_langbar_post(self,i):
        """
        get the html for the langbar of post i (using reloc to always point well)
        """        
        res=''
        page=self.postlist[i]
        for lang in self.langlist:
            if len(self.get_langage_str(lang)):
                adress=page['filename_nolang']+'.'+self.get_langage_str(lang)
            else:
                adress=page['filename_nolang']
            if find_page(adress,self.postlist):
                text=self.config['LangBar'][lang]['text'].format(reloc=page['reloc'])
                #print '{0}'.format(self.config['LangBar'][lang]['text'])
                res+=u'<a href="{adress}_post.html">{text}</a>{sep}'.format(adress=page['reloc']+unicode(adress),text=unicode(text),sep=unicode(self.config['LangBar']['separator']))
        return res
        
    def generate_website(self):
        """
        generate all pages using the corresponding templates.
        
        list of performed tasks:
            - content for each page and post is obtained (using specified markup langage)
            - all pages are written using the selected template
            - if posts are to be generated, then generate them
            - cappy all files corresponding to the patterns
            - generate sitemap is required
        """
        
        # generate pages content using the selcted makup langage
        self.get_pages_content()
        
        # check existing directories in output
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)
        for path in self.listdir:
            path=path.replace(self.srcdir,self.outdir)
            if not os.path.isdir(path):
                os.mkdir(path)  
                
        for page in self.pagelist:
            #print "Generating page: {page}".format(page=self.outdir+os.sep+page['filename']+'.html')
            page['raw_page']=self.templates[page['template']].render(pagelist=self.pagelist,postlist=self.postlist,postlist_lan=self.postlist_lan,ext=self.ext,**page)
            #print page['raw_page']
            f=codecs.open(self.outdir+os.sep+page['filename']+'.html',mode='w', encoding="utf8")
            f.write(page['raw_page'])
            f.close()

        if self.config['General']['generate_posts']=='True':
            for page in self.postlist:
                #print "Generating post: {page}".format(page=self.outdir+os.sep+page['filename']+'_post'+'.html')
                page['raw_page']=self.templates[page['template']].render(pagelist=self.pagelist,postlist_lan=self.postlist_lan,ext=self.ext,postlist=self.postlist,**page)
                #print page['raw_page']
                f=codecs.open(self.outdir+os.sep+page['filename']+'_post'+'.html',mode='w', encoding="utf8")
                f.write(page['raw_page'])
                f.close()
        
        for pattern in self.config['Pattern']['Copy']['list']:
            for files in glob.glob(self.srcdir+os.sep+pattern):
                file2=files.replace(self.srcdir,self.outdir)
                # copy only if modified or not exists
                if not os.path.isfile(file2):
                    shutil.copy(files,file2)
                elif os.path.getmtime(file2)<os.path.getmtime(files):
                    shutil.copy(files,file2)
                        
                
        # sitemap
        if self.config['General']['generate_sitemap']:
            #print "Generating sitemap for {nb} pages".format(nb=len(self.pagelist))
            smap=u'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            smap+=get_sitemap_url(self.config['General']['base_url'],'weekly',lastmod=datetime.date.today().isoformat(),priority=1)
            for page in self.pagelist:
                smap+=get_sitemap_url(self.config['General']['base_url']+page['filename']+'.html',lastmod=page['date'])
            smap+='</urlset>'
            f=codecs.open(self.outdir+os.sep+'sitemap'+'.xml',mode='w', encoding="utf8")
            f.write(smap)
            f.close()
             

        
        
        #print self.pagelist

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
        
        self.links=self.get_links()
        
        # loading pages
        for page in recursiveglob(self.srcdir,'*.page'):
            temp=dict()
            
            init_page_properties(temp)
            
            # page name extraction
            temp['srcname']=page
            temp['relscrname']=temp['srcname'].replace(self.srcdir+os.sep,'')
            (root, ext)=os.path.splitext(temp['relscrname'])
            temp['filename']=root
            temp['markup']=self.config['General']['default_markup']

            # langage extraction
            temp['lang'],temp['filename_nolang']=get_page_langage(temp['relscrname'],self.config['General']['lang'])  
            if len(self.get_langage_str(temp['lang'])):
                temp['template']=self.config['General']['default_template']+'.'+self.get_langage_str(temp['lang'])
            else:
                temp['template']=self.config['General']['default_template']
            
            # relative position in the website
            nbdir=temp['relscrname'].count('/')
            for i in range(nbdir):
                temp['reloc']+='../'
                
            temp['website_name']=self.config['General']['base_name']
            temp['website_subname']=self.config['General']['base_subname']
            temp['website_author']=self.config['General']['base_author']
            temp['website_url']=self.config['General']['base_url']
            temp['links']=self.links
            
            tatbuf = os.stat(page)
            temp['date']=datetime.date.fromtimestamp(tatbuf.st_mtime).isoformat()
            # read page content
            f= codecs.open(page, mode="r", encoding="utf8")
            temp['raw_file']=f.readlines()
            f.close()
            #print temp
            # get properties from file
            get_page_properties(temp,temp['raw_file'])
            temp['raw_text']=temp['raw_text'].replace('](/','](' +temp['reloc'])
            #print temp
  
            self.pagelist.append(temp)
            
        self.pagelist.sort(key=lambda k: k['sort_info'])
        self.set_links_to_lang()
            
        # loading posts
        for post in recursiveglob(self.srcdir,'*.post'):

            temp=dict()
            init_page_properties(temp)
            
            # page name extraction
            temp['srcname']=post
            temp['relscrname']=temp['srcname'].replace(self.srcdir+os.sep,'')
            (root, ext)=os.path.splitext(temp['relscrname'])
            temp['filename']=root
            temp['markup']=self.config['General']['default_markup']

            # langage extraction
            temp['lang'],temp['filename_nolang']=get_page_langage(temp['relscrname'],self.config['General']['lang'])  
            if len(self.get_langage_str(temp['lang'])):
                temp['template']=self.config['General']['default_template']+'.'+self.get_langage_str(temp['lang'])
            else:
                temp['template']=self.config['General']['default_template']
            
            # relative position in the website
            nbdir=temp['relscrname'].count('/')
            for i in range(nbdir):
                temp['reloc']+='../'
            temp['reloc']=self.config['General']['base_url']
            

            tatbuf = os.stat(post)
            temp['date']=datetime.date.fromtimestamp(tatbuf.st_mtime).isoformat()
                      
            
            # read page content
            f= codecs.open(post, mode="r", encoding="utf8")
            temp['raw_file']=f.readlines()
            f.close()
            #print temp
            # get properties from file
            get_page_properties(temp,temp['raw_file'])
            temp['raw_text']=temp['raw_text'].replace('](/','](' +self.config['General']['base_url'])
            
            self.postlist.append(temp)      
            
        self.postlist.sort(key=lambda k: k['date'],reverse=True)    
        
        
        
        # preparing templates (in dictionnary)
        self.env= jinja2.Environment(loader=jinja2.FileSystemLoader(self.templdir))
        for template in recursiveglob(self.templdir,'*.template'):
            template=template.replace(self.templdir+os.sep,'')
            (head, tail)=os.path.split(template)
            (root, ext)=os.path.splitext(tail)
            temp=self.env.get_template(template)
            self.templates[root]=temp

            

                 



def main(argv):  

    parser = argparse.ArgumentParser(prog='pywebgen',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''pywebgen is a python version of the webgen generator''',
    epilog='''''')   
    
    parser.add_argument('-c','--configfile', type=str, nargs=1,
                   help='the task that should be performed',action="store",default=c_file)                 
                   
    args= parser.parse_args()   
    
    config=load_config(args.configfile)
    
    if config==None:
        print 'bad config file format'
    elif not config:
        print 'no config file'       
    else:
        site=website(args.configfile)
        site.generate_website()

def test():   
   import doctest
   doctest.testmod(verbose=True)

    
    

if __name__ == "__main__":
   #import doctest
   #doctest.testmod(verbose=True)   
   main(sys.argv[1:])