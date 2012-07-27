# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""
import datetime
try:
    from pybtex.database.input import bibtex
except ImportError:
    bibtex=None 
    print "bibtex plugin: pybtex not installed, no ref list will be generated"

# name of the plugin
plug_name='bibtex'


latex_convert=[[u'\\v{',u''],
          [u'\\_',u'_'],
          [u'\\c{c}',u'ç'],
          [u'\\{',u'\\ocb'],# tweak pour pouvoir toujour avoir des curls
          [u'\\}',u'\\ccb'],          
          [u'{',u''],
          [u'}',u''],
          [u'\\ocb',u'{'],
          [u'\\ccb',u'}'], 
          [u'\\\'e',u'é'],
          [u'\\`e',u'è'],
          [u'\\\'o','o'],
          [u'\\"u',u'ü'], 
          [u'\\"o',u'ö'],
          [u'\\"a',u'ä'],
          [u'\\`a',u'à'],
          [u'\\~n','n'],
          [u'\\&','&'],
          [u'\\\'a','a'], ]

field_list=['author',
            'title',
            'year',
            'journal',
            'booktitle',
            'howpublished',
            'institution',
            'school',
            'number',
            'pages',
            'volume',
            'publisher',
            'organization',
            'url',
            'school',
            'abstract',
            'key',
            'file',
            'pdf',            
            'code',
            'pres',
            'pubtype']   
            

def unlatexit(chaine):
    # remove the most obvious latex commands..
    chaine=unicode(chaine)
    if not chaine =='':
        for key in latex_convert:
            chaine=unicode(chaine.replace(key[0],key[1])) 
    return (chaine)
    
def tryget(item,field):
    try:         
        res=item[field]
    except (KeyError):
        res=""
    return res
        
def prep_ref(ref):
    for field in field_list:
        ref[field]=unlatexit(tryget(ref,field))

def load_bibfile(fname,recentyears=3):
    bib=list()
    if bibtex:
        parser = bibtex.Parser()
        bib_data = parser.parse_file(fname)
        
        year=datetime.date.today().year
        reentyears=list()
        for i in range(recentyears):
            reentyears.append(str(year-i))
    
        for key in bib_data.entry_keys:
            temp=bib_data.entries[key].fields
            temp['key']=key
            temp['type']=bib_data.entries[key].type
            #print temp['type']
            temp['author']=bib_data.entries[key].fields['author']
            temp['author_tex']=temp['author']
            temp['author']=temp['author'].replace(' and ',', ')
            prep_ref(temp)
            temp['journalproc']=temp['journal']+temp['booktitle']+temp['howpublished']+temp['school']
            temp2=''
            if not temp['volume']=='':
                temp2+=' Vol. '+temp['volume']+','
            if not temp['number']=='':
                temp2+=' N. '+temp['number']+','             
            if not temp['pages']=='':
                temp2+=' pp '+temp['pages']+','
            temp['volnumpage']=temp2[:-1];
            temp['recentyears']=reentyears
            #print temp
            bib.append(temp)
        bib.sort(key=lambda k: k['year'],reverse=True)
    
    return bib

def plugin_change_lists(website):
    """
    function that adds information to website.pagelist
    and website.postlist
    """
    pass

def plugin_return(config):
    """
    returns the plugin 
    """
    fname=   config['Plugins'][plug_name]['bibfile']
    res=load_bibfile(fname)
    return res
    
    
    
    