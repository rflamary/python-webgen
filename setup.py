#!/usr/bin/env python

from distutils.core import setup
import os
import glob

import webgen._version as version

ROOT = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(ROOT, 'README.md')).read()

pte='pywebgen-example'

setup(name='python-webgen',
      version=version.__version__,
      description='static website generation',
      long_description=README,
      author=u'Remi Flamary',
      author_email='remi.flamary@gmail.com',
      url='https://github.com/rflamary/python-webgen',
      packages=['webgen','webgen.plugins'],
      platforms=['linux'],
      license = 'GPL',
      scripts=['pywebgen'],
      data_files=[(pte, ['example/website.cfg','example/Makefile','README.md']),
                  (pte+os.sep+'src',glob.glob('example/*/*.page')),
                  (pte+os.sep+'templates',glob.glob('example/templates/*.template')),
                  (pte+os.sep+'templates',glob.glob('example/templates/*.html')),
                  (pte+os.sep+'src'+os.sep+'css',glob.glob('example/src/*/*.css')),
                  (pte+os.sep+'src'+os.sep+'bib',glob.glob('example/src/*/*.bib')),
                  (pte+os.sep+'src',glob.glob('example/src/*.csv')),
                  (pte+os.sep+'src'+os.sep+'images',glob.glob('example/*/*.png')),
                  (pte+os.sep+'src'+os.sep+'news',glob.glob('example/src/news/*.post'))],
      requires=["argparse (>=0.1)","configobj (>=4.7)","jinja2 (>= 2.6)","markdown (>= 2.1)"],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
     )
