Webgen.py
=========

Webgen.py is a Python version of the well known [webgen](http://webgen.rubyforge.org/) static website generator. It is not a complete rewrite of webgen and some features are missing but there are also a few new nice things. The main reason webgen.py exists is because i did not know ruby and changing things with webgen is a pain so i decided to use my own python generator.

## Features

* Quick generation of multilingual (.en.page, .fr.page) static websites.
* Compatibility with webgen site architecture (.page format).
* Clean and easy site architecture (one .page file == one html file)
* More readable configuration file (no more yaml).
* Jinja2 templates for generation (selectable per page, templating in page).
* Provides a coarse blog post handler (posts can be printed through template loops, no tags yet)
* All properties set in the .page header can be used in the template
* Modular plugin system ()
* Easy python plugin in subfolder (no system installation needed)

Plugins:

* Links list configurable in the config file.
* Language menu.
* Website sitemap.xml automatically generated.
* Automatic reference page generation from bibtex file.
* Print list from csv file.
* Zorglangue page generation (from french).

Markdown plugins:

* Can be used (when listed in config file) from subfolder mdextensions.
* Can use latex formulas with 'latex' extension but requires latex and dvipng 


Less desirable features:

* Only Markdown markup langage for now (should be easy to change anyway).
* Does not work out of the box on a webgen site (config file and template have to be adapted)
* No hierachical menu, all pages in menu have the same level 
* Not extremely tested.

## Installation

### Required python modules
The file webgen.py is self content but some python modules are required:

* argparse (>=0.1)
* configobj (>=4.7)
* jinja2 (>= 2.6)
* markdown (>= 2.1)

Those can be easily installed on debian-based linux with:

	apt-get install python-argparse python-configobj python-jinja2 python-markdown 
	
	
### Testing

The github repository contains a demo website with:

* *config.cfg* a demo config file
* *templates* folder containing templates for the demo website
* *src* source architecture and content for the website

Execute webgen.py in the folder for generating the website in the *out* folder:

	$ ./webgen.py
	
The markdown 'latex' extension is not used by default, to activate it, add 'latex' to markdown extensions in the configuration file.	
	
## Documentation

Right now documentation is nearly non-existent but the website architecture is the same as for webgen. And the python code is not so long yet.

	
	

