include ../../Makefile.omd

NAME = freetds
FREETDS_VERSION = 0.91
FREETDS_DIR = freetds-$(FREETDS_VERSION)
SHELL = /bin/bash

build:
	# ftp://ftp.freetds.org/pub/freetds/stable/freetds-stable.tgz
	tar xf freetds-$(FREETDS_VERSION).tar.gz
	cd $(FREETDS_DIR) && patch -p1 < ../0001-ct_connect-allow-host.patch
	cd $(FREETDS_DIR) && \
	./configure --prefix=$(OMD_ROOT) && \
	$(MAKE) && $(MAKE) DESTDIR=$(shell pwd)/tmpinstall install

install:
	$(MAKE) DESTDIR=$(DESTDIR) -C $(FREETDS_DIR) -j 1 install
	rm -rf $(DESTDIR)$(OMD_ROOT)/etc/freetds.conf
	rm -rf tmpinstall

skel:

clean:
	rm -rf $(FREETDS_DIR)
	rm -rf tmpinstall
