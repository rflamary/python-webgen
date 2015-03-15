# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""


import string
import copy,codecs,os
import re,datetime

         

lst_prop_init=[['links',''],]

plug_name='links'


def get_links(config):
    """
    get html list of links to be included in the pages
    """
    res="<ul>\n"
    for lnk in config[plug_name]['list']:
        res+=u'\t\t<li class="{classe}"><a href="{url}" title="{txt}">{txt}</a></li>\n'.format(classe=config[plug_name]['class_li_link'],txt=lnk,url=config[plug_name]['list'][lnk])
    res+="</ul>\n"        
    return res
     

   
def plugin_change_lists(website):
    """
    function that can modify the whole website (before content generation)
    """
    txt=get_links(website.config)
    for page in website.pagelist:
        page[plug_name]=txt         

def plugin_change_lists_post(website):
    """
    function that can modify the whole website (after content generation)
    """
    pass


def plugin_return(config):
    """
    returns the plugin 
    """
    res=get_links(config)
    return res
    
    
    
    