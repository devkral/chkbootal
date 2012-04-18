ROOTDIR=""
SYSTEMD=$(ROOTDIR)/usr/lib/systemd/system
BINDIR=$(ROOTDIR)/usr/bin

#SEDJUST=sed "s|/usr/bin/|$BINDIR|" -s systemd/chkbootal.service
#RM=rm -f
#CP=cp




all : mainscri sysd

sysd : mainscri
	sed "s|/usr/bin|$(BINDIR)|" systemd/chkbootal-boot.service > $(SYSTEMD)/chkbootal-boot.service
	sed "s|/usr/bin|$(BINDIR)|" systemd/chkbootal-stop.service > $(SYSTEMD)/chkbootal-stop.service

mainscri :
	cp src/chkbootal.py $(BINDIR)


uninstall :
	rm $(BINDIR)/chkbootal.py
	rm $(SYSTEMD)/chkbootal-boot.service
	rm $(SYSTEMD)/chkbootal-stop.service
