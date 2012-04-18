ROOTDIR=""
SYSTEMD=$(ROOTDIR)/usr/lib/systemd/system
BINDIR=$(ROOTDIR)/usr/bin

SEDJUST=sed "s/\usr\/bin\//$BINDIR/" -s systemd/chkbootal.service
RM=rm -f
CP=cp

all:	$(CP) systemd/* $(SYSTEMD)
	$(CP) src/* $(BINDIR)

