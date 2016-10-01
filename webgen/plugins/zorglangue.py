# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:41:48 2012

@author: flam
"""
from builtins import str

import io
import sys
import string
import copy
import re
plug_name='zorglangue'


lstsplit=["\n",".",";",",","-","'","?","!",'-','(',')'," "]

def zorglangue(text="Vive Zorglub!"):
    res=[text]
    tree=get_tree([text],lstsplit)
    tree=zorg_tree(tree)
    res=un_tree(tree[0],lstsplit)
    return res

word_re = re.compile(r'\b\w+\b')

def zorglang(text):
    with io.StringIO() as buf:
        last_index = 0
        for match in word_re.finditer(text):
            buf.write(text[last_index:match.start()])
            word = match.group()
            for i in range(len(word)):
                if word[i].isupper():
                    buf.write(word[-1 - i].upper())
                elif word[i].islower():
                    buf.write(word[-1 - i].lower())
                else:
                    buf.write(word[-1 - i])
            last_index = match.end()
        buf.write(text[last_index:])
        return buf.getvalue()



def get_tree(text,lst):
    res=text
    #print text
    #print lst
    #print isinstance(text, list)
    if len(lst)and isinstance(text, list):# and isinstance(text, list)
        sep=lst[0]
        #print sep
        res=[get_tree(sub.split(sep),lst[1:]) for sub in text]
    #print res
    return res

def un_tree(tree,lst):
    res=tree
    #print lst
    #print res
    if len(lst) and isinstance(tree, list):
        sep=lst[0]
        res=[un_tree(sub,lst[1:]) for sub in tree]
        #print res
        #print sep
        res=sep.join(res)
    return res

def zorg_tree(tree):
    if isinstance(tree, list):# and isinstance(text, list)
        res=[zorg_tree(sub) for sub in tree]
    else:
        res=zorg_word(tree)
    return res

def zorg_word(word):

    if word.isalpha():
        if word[0].isupper() and word[1:].lower()==word[1:]:
            temp=word[::-1]
            word=word[-1].upper()+ temp[1:-1]+word[0].lower()
        else:
            word=word[::-1]
    return word

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
    lang='zl'
    #zorglangue=zorglang
    for page in website.pagelist:
        if page['lang']=='fr':

            adress=page['filename_nolang']
            text=website.config['langbar'][lang]['text'].format(reloc=page['reloc'])
            page['langbar']=page['langbar']+u'<a href="{adress}.zl.html">{text}</a>{sep}'.format(adress=page['reloc']+str(adress),text=str(text),sep=str(website.config['langbar']['separator']))

            temp=copy.deepcopy(page)
            temp['content']= temp['content'].replace('<',' <')
            temp['content']= temp['content'].replace('>','> ')

            temp['content']= re.sub("<a.*?>", " ", temp['content'])
            #temp['raw_text']=zorglangue(temp['raw_text'])
            temp['content']=zorglangue(str(temp['content']))
            temp['lang']='zl'
            temp['filename']=temp['filename'].replace('.fr','.zl')
            temp['menu']=temp['menu'].replace('.fr','.zl')
            temp['title']=zorglangue(temp['title'])
            temp['website_name']=zorglangue(temp['website_name'])
            temp['website_subname']=zorglangue(temp['website_subname'])
            temp['template']='default.zl'
            temp2={'url':page['reloc']+str(adress),'lang':'zl'}
            for key in website.config['langbar']['zl']:
                temp2[key]=website.config['langbar']['zl'][key]
            page['langlist'].append(temp2)
            ptemp.append(temp)

            pass
        else:
            adress=page['filename_nolang']
            text=website.config['langbar'][lang]['text'].format(reloc=page['reloc'])
            page['langbar']=page['langbar']+u'<a href="{adress}.zl.html">{text}</a>{sep}'.format(adress=page['reloc']+str(adress),text=str(text),sep=str(website.config['langbar']['separator']))

            temp={'url':page['reloc']+str(adress),'lang':'zl'}
            for key in website.config['langbar']['zl']:
                temp[key]=website.config['langbar']['zl'][key]
            page['langlist'].append(temp)

    for temp in ptemp:
        website.pagelist.append(temp)
    website.set_links_to_lang()
    #print len(website.pagelist)


def plugin_return(config):
    """
    returns the plugin
    """
    res='Vive Zorglub'
    return res
