from __future__ import absolute_import

# import all plugins and set a dictionary for selection
from . import bibtex
from . import copyfile
from . import csvload
from . import langbar
from . import links
from . import menu
from . import sitemap
from . import zorglangue

plug_list={'bibtex':bibtex,
           'copyfile':copyfile,
           'csvload':csvload,
           'langbar':langbar,
           'links':links,
           'menu':menu,
           'sitemap':sitemap,
           'zorglangue':zorglangue}