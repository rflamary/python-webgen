# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012
import datetime
@author: flam
"""
import datetime
import codecs



# name of the plugin
plug_name='bibtex'


latex_fr=[[u'\\v{',u''],
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
          [u'\\\'a','a'],
          [u'"',''],  ]

bibsep=[["{","}"]]

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
        for key in latex_fr:
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

def load_bibfile2(fname):
    
    #f = open(fname, "r")
    f = codecs.open(fname, "r", "utf-8")
    
    lines=f.readlines()
    
    return get_biblist(lines)

def get_biblist(lines):
    bib=list()
    
    temp=dict()
    
    inref=False
    inkey=False
    
    #f= codecs.open('index2.html', "w", "utf-8")
    
    for l in lines:
        
        if l:        
            # if not in a current ref we search for a new entry
            if not inref:
                if l[0]=='@':#entry found
                    lst=l[1:].split('{')
                    t=lst[0] # get the pub type
                    ktemp=lst[1].split(',') # get rid of after the ,
                    #f.write(ktemp[0]+ '\n')
                    inref=True
                    temp=dict() # dictionnary 
                    temp['type']=t.lower()
                    temp['key']=ktemp[0]
            else:
                if l[0]=='}': # closing ref (necessary t)
                    prep_ref(temp)
                    bib.append(temp)
                    inref=False    
                else:
    
                    if not inkey:    # not locked in an opened key      
                        lst=l.split('=') # separate key and value
                        key=lst[0].replace(' ','')
                        val=u''.join(lst[1:])
                        while val[-1]=='\n' or val[-1]==',' or val[-1]==' ' or val[-1]=='\r':
                            val=val[:-1]
                        temp[key]=val
                        #f.write('\t'+ key + ' : ' + unlatexit(val)+'\n')
                        if not l.count('{')==l.count('}'):
                            opendif=l.count('{')-l.count('}')
                            inkey=True
                    else:
                        val+=l
                        temp[key]=val
                        if l.count('{')+opendif==l.count('}'):
                            inkey=False
                            while val[-1]=='\n' or val[-1]==',' or val[-1]==' ' or val[-1]=='\r':
                                val=val[:-1]
                                temp[key]=val
                        else:
                            opendif+=l.count('{')-l.count('}')
                
    return bib

def load_bibfile(fname,recentyears=3):
    bib=list()

    bib=load_bibfile2(fname)
    #print bib

    
    year=datetime.date.today().year
    reentyears=list()
    for i in range(recentyears):
        reentyears.append(str(year-i))

    for temp in bib:
        temp['recentyears']=reentyears
        #print temp
        
    bib.sort(key=lambda k: k['year'],reverse=True)
    
    return bib



def plugin_return(config):
    """
    returns the plugin after website loading and store the data in ext['plugname'] for use in template
    """
    fname=   config['Plugins'][plug_name]['bibfile']
    res=load_bibfile(fname)
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
        
