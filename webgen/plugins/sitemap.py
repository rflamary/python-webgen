# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""


import string
import copy,codecs,os
import re,datetime

def to_bool(string):
    """
    crapy str to boolean conversion function to stay compatible with webgen
    """
    if string=='true' or string=='True' or string=='1':
        return True
    else:
        return False            

lst_prop_init=[['in_sitemap','true'],
               ['sitemap_priority',.5],
               ['sitemap_frequency','weekly'],]
               
lst_prop_convert=[['sitemap_priority',float],         
                  ['in_sitemap',to_bool],  ]             


   

plug_name='sitemap'



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
     

   
def plugin_change_lists(website):
    """
    function that can modify the whole website (before content generation)
    """
    pass        

def plugin_change_lists_post(website):
    """
    function that can modify the whole website (after content generation)
    """
    #print len(website.pagelist)
    ptemp=list()
    smap=u'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    smap+=get_sitemap_url(website.config['General']['base_url'],'weekly',lastmod=datetime.date.today().isoformat(),priority=1)
    for page in website.pagelist:
        if page['in_sitemap']:
            smap+=get_sitemap_url(website.config['General']['base_url']+page['filename']+'.html',lastmod=page['date'])
    smap+='</urlset>'
    f=codecs.open(website.outdir+os.sep+'sitemap'+'.xml',mode='w', encoding="utf8")
    f.write(smap)
    f.close()        
    #print len(website.pagelist)


def plugin_return(config):
    """
    returns the plugin 
    """
    res=plug_name
    return res
    
    
    
    