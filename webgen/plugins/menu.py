# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""


import string
import copy,codecs,os
import re,datetime

plug_name='menu'     

lst_prop_init=[['menu',''],
               ['in_menu','false'],]
               
def to_bool(string):
    """
    crapy str to boolean conversion function to stay compatible with webgen
    """
    if string=='true' or string=='True' or string=='1':
        return True
    else:
        return False

lst_prop_convert=[['in_menu',to_bool], ] 



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

def get_menu(website,menulist,i):
    """
    get html menu with pages selected in menulist for page i (index).
    the selected page is not a link and has a different il class
    """
    res="<ul>\n"
    rel=website.pagelist[i]['reloc']
    for j in menulist:
        page=website.pagelist[j]
        if j==i:
            res+=u'\t\t<{li} class="{classe}"><span>{title}</span></{li}>\n'.format(classe=website.config[plug_name]['class_li_current'],title=page['title'],li=website.config[plug_name]['li'])
        else:
            res+=u'\t\t<{li} class="{classe}"><a href="{adress}.html">{title}</a></{li}>'.format(classe=website.config[plug_name]['class_li_other'],title=page['title'],adress=rel+page['filename'],li=website.config[plug_name]['li'])
    res+="</ul>\n"
    return res
    
    
def get_menu_post(website,menulist,i):
    """
    get html menu with pages selected in menulist for post i (index)
    no pages are select in this case
    """        
    res="<ul>\n"
    rel=website.postlist[i]['reloc']
    for j in menulist:
        page=website.pagelist[j]
        res+=u'\t\t<li class="{classe}"><a href="{adress}.html">{title}</a></li>'.format(classe=website.config[plug_name]['class_li_other'],title=page['title'],adress=rel+page['filename'])
    res+="</ul>\n"
    return res


def set_menus_langbar(website):
    """
    add the 'menu' and 'langbar' key containt html list to all pages 
    """
    
    # list used langages
    langlist=list()
    for page in website.pagelist:
        if not page['lang'] in langlist:
            langlist.append(page['lang'])
            
    website.langlist=langlist

    # create list of menus per lang  and per page      
    for lang in langlist:
        menulist=list()
        for i in range(len(website.pagelist)):
            page=website.pagelist[i]
            if page['lang']== lang and page['in_menu'] :
                menulist.append(i)
        # for all pages
        for i in range(len(website.pagelist)):
            page=website.pagelist[i]
            if page['lang'] == lang:
                page['menu']=get_menu(website,menulist,i) 
                
        # for all posts
        for i in range(len(website.postlist)):
            page=website.postlist[i]
            if page['lang'] == lang:
                page['menu']=get_menu_post(website,menulist,i)         

                


   
def plugin_change_lists(website):
    """
    function that can modify the whole website (before content generation)
    """
    set_menus_langbar(website)


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
    
    
    
    
