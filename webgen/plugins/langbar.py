# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""
from builtins import str
from builtins import range


lst_prop_init=[['langbar',''],]

plug_name='langbar'

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


def get_langbar(website,i):
    """
    get the html for the langbar of page i (using reloc to always point well)
    """
    res=''
    page=website.pagelist[i]
    for lang in website.langlist:
        if len(website.get_langage_str(lang)):
            adress=page['filename_nolang']+'.'+website.get_langage_str(lang)
        else:
            adress=page['filename_nolang']
        if find_page(adress,website.pagelist):
            text=website.config[plug_name][lang]['text'].format(reloc=page['reloc'])
            #print '{0}'.format(self.config['LangBar'][lang]['text'])
            res+=u'<a href="{adress}.html">{text}</a>{sep}'.format(adress=page['reloc']+str(adress),text=str(text),sep=str(website.config[plug_name]['separator']))
    return res



def get_langlist(website,i):
    """
    get the html for the langbar of page i (using reloc to always point well)
    """
    res=list()
    page=website.pagelist[i]
    for lang in website.langlist:
        if len(website.get_langage_str(lang)):
            adress=page['filename_nolang']+'.'+website.get_langage_str(lang)
        else:
            adress=page['filename_nolang']
        if find_page(adress,website.pagelist):
            temp=dict()
            temp['lang']=lang
            temp['url']=page['reloc']+str(adress)+'.html'
            for key in website.config[plug_name][lang]:
                temp[key]=website.config[plug_name][lang][key]
            #print '{0}'.format(self.config['LangBar'][lang]['text'])
            res.append(temp)
    return res
        
def get_langbar_post(website,i):
    """
    get the html for the langbar of post i (using reloc to always point well)
    """        
    res=''
    page=website.postlist[i]
    for lang in website.langlist:
        if len(website.get_langage_str(lang)):
            adress=page['filename_nolang']+'.'+website.get_langage_str(lang)
        else:
            adress=page['filename_nolang']
        if find_page(adress,website.postlist):
            text=website.config[plug_name][lang]['text'].format(reloc=page['reloc'])
            #print '{0}'.format(self.config['LangBar'][lang]['text'])
            res+=u'<a href="{adress}_post.html">{text}</a>{sep}'.format(adress=page['reloc']+str(adress),text=str(text),sep=str(website.config[plug_name]['separator']))
    return res
     
def get_langlist_post(website,i):
    """
    get the html for the langbar of page i (using reloc to always point well)
    """
    res=list()
    page=website.postlist[i]
    for lang in website.langlist:
        if len(website.get_langage_str(lang)):
            adress=page['filename_nolang']+'.'+website.get_langage_str(lang)
        else:
            adress=page['filename_nolang']
        if find_page(adress,website.pagelist):
            temp=dict()
            temp['lang']=lang
            temp['url']=page['reloc']+str(adress)+'.html'
            for key in website.config[plug_name][lang]:
                temp[key]=website.config[plug_name][lang][key]
            #print '{0}'.format(self.config['LangBar'][lang]['text'])
            res.append(temp)
    return res     
   
def plugin_change_lists(website):
    """
    function that can modify the whole website (before content generation)
    """
    langlist=list()
    for page in website.pagelist:
        if not page['lang'] in langlist:
            langlist.append(page['lang'])
    website.langlist=langlist   
    
    
    postlist_lan=dict()
    # create list of menus per lang  and per page      
    for lang in langlist:
        postlist_lan[lang]=list()
        for i in range(len(website.pagelist)):
            page=website.pagelist[i]
        # for all pages
        for i in range(len(website.pagelist)):
            page=website.pagelist[i]
            if page['lang'] == lang:
                page['langbar']=get_langbar(website,i)
                page['langlist']=get_langlist(website,i)
        # for all posts
        for i in range(len(website.postlist)):
            page=website.postlist[i]
            if page['lang'] == lang:                  
                page['langbar']=get_langbar_post(website,i)
                page['langlist']=get_langlist_post(website,i)


def plugin_change_lists_post(website):
    """
    function that can modify the whole website (after content generation)
    """
    pass


def plugin_return(config):
    """
    returns the plugin 
    """
    res=plug_name
    return res
    
    
    
    
