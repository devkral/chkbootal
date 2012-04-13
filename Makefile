ROOTDIR=""
SYSTEMD=$(ROOTDIR)/usr/lib/systemd/system
BINDIR=$(ROOTDIR)/usr/bin
SYSTEMD_FILE1=chkboot-bootcheck.service
SYSTEMD_FILE2=chkboot-shutdownsafe.service
BIN_FILE1=src/bootcheck.sh
BIN_FILE2=shutdownsafe.sh

SEDJUST=sed "s/\usr\/bin\//$BINDIR/" -s $SYSTEMD_FILE1 $SYSTEMD_FILE2
RM=rm -f
CP=cp

all:	$(CP) $(SYSTEMD_FILE1) $(SYSTEMD)
	$(CP) $(SYSTEMD_FILE2) $(SYSTEMD)
	$(CP) $(BIN_FILE1) $(BINDIR)
	$(CP) $(BIN_FILE2) $(BINDIR)

