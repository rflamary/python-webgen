# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""
import datetime
import codecs

# name of the plugin
plug_name='csvload'


            
def load_csv_files(files,sep):
    
    res=list()
    for f in files:
        res.append(load_csv(f,sep))
    return res
    
def load_csv(fname,sep):
    f = codecs.open(fname, "r", "utf-8")

    res=list()
    
    for line in f:
        #print line
        s=line.split(sep)
        res.append(s)
        
        
    f.close()
    return res


def plugin_return(config):
    """
    returns the plugin after website loading and store the data in ext['plugname'] for use in template
    """
    files= config[plug_name]['files']
    sep=   config[plug_name]['sep']
 
    res=load_csv_files(files,sep)

    return res
    
def plugin_change_lists(website):
    """
    function that can modify the whole website (before content generation)
    """
    pass    
    
def plugin_change_lists_post(website):
    """
    function that can modify the whole website (after content generation)
    """
    pass    
        
