include ../../Makefile.omd

NAME = mk-livestatus
VERSION = 1.2.8p15
DIR = $(NAME)-$(VERSION)

CONFIGUREOPTS = \
    --prefix=$(OMD_ROOT)

ifneq (,$(findstring SLES 11SP4,$(DISTRO_INFO)))
export CC := gcc-4.8
export CXX := g++-4.8
else ifneq (,$(findstring SLES 11SP,$(DISTRO_INFO)))
export CC := gcc-4.7
export CXX := g++-4.7
endif

build:
	tar xzf $(DIR).tar.gz
	cd $(DIR) ; ./configure $(CONFIGUREOPTS)
	$(MAKE) -C $(DIR) all

install:
	$(MAKE) DESTDIR=$(DESTDIR) -C $(DIR) install
	mkdir -p $(DESTDIR)$(OMD_ROOT)/bin
	install -m 755 lq $(DESTDIR)$(OMD_ROOT)/bin
	mkdir -p $(DESTDIR)$(OMD_ROOT)/lib/python
	install -m 644 $(DIR)/api/python/livestatus.py $(DESTDIR)$(OMD_ROOT)/lib/python

skel:

clean:
	rm -rf mk-livestatus-*.*.*[0-9]

upstream:
	if [ ! -e mk-livestatus-$(VERSION).tar.gz ] ; then \
	  git rm mk-livestatus-*.tar.gz || true ; \
	  rm -f mk-livestatus-*.tar.gz ; \
	  wget http://mathias-kettner.de/download/mk-livestatus-$(VERSION).tar.gz ; \
	  git add mk-livestatus-$(VERSION).tar.gz ; \
	fi
