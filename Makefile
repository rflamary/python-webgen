

OUTPUTDIR=out




all: html
	

help:
	@echo 'Makefile for a my Web site                                            '
	@echo '                                                                      '
	@echo 'Usage:                                                                '
	@echo '   make html                        (re)generate the web site         '
	@echo '   make view                        open navigator                    '
	@echo '   make htmlview                    generate and view                 '
	@echo '   make clean                       remove the generated files        '
	@echo '        

htmlview: html view

html: 
	./webgen.py

clean:
	rm -fr $(OUTPUTDIR)
	
	
view:
	xdg-open out/index.html


.PHONY: html help clean ftp_upload 
    
