#!/usr/bin/env python

from distutils.core import setup
import os
import glob

import webgen._version as version

ROOT = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(ROOT, 'README.md')).read()

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
      data_files=[('', ['example/website.cfg','example/Makefile','README.md']),
                  ('',glob.glob('example/*/*.page')),
                  ('',glob.glob('example/*/*.template')),
                  ('',glob.glob('example/*/*.html')),
                  ('',glob.glob('example/*/*/*.css')),
                  ('',glob.glob('example/*/*/*.bib')),
                  ('',glob.glob('example/*/*.csv')),
                  ('',glob.glob('example/*/*/*.png')),
                  ('',glob.glob('example/*/*/*.post'))],
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
