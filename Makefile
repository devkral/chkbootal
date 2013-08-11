NAME=chkbootal
EXTENSION=.py
INSTALLDIR=/usr/bin
SYSTEMD=/usr/lib/systemd/system
CHKDIR=/boot
CHKSAVEDIR=/var/chkboot



all : install

install:  sysd

sysd : mainscript
	sed -e "s|/usr/bin/chkbootal.py|$(INSTALLDIR)/$(NAME)$(EXTENSION)|" -e "s|Also=chkbootal|Also=$(NAME)|" systemd/chkbootal-boot.service > $(SYSTEMD)/$(NAME)-boot.service
	sed -e "s|/usr/bin/chkbootal.py|$(INSTALLDIR)/$(NAME)$(EXTENSION)|" -e "s|Also=chkbootal|Also=$(NAME)|" systemd/chkbootal-stop.service > $(SYSTEMD)/$(NAME)-stop.service

mainscript :
	install -D -m755 src/chkbootal.py $(INSTALLDIR)/$(NAME)$(EXTENSION)
	sed -i -e "s|/boot|$(CHKDIR)|" $(INSTALLDIR)/$(NAME)$(EXTENSION)
	sed -i -e "s|/var/chkboot|$(CHKSAVEDIR)|" $(INSTALLDIR)/$(NAME)$(EXTENSION)
	sed -i -e "s|/usr/bin/systemctl reboot|$(REBOOT)|" $(INSTALLDIR)/$(NAME)$(EXTENSION)


uninstall :
	rm $(BINDIR)/$(NAME)
	rm $(SYSTEMD)/$(NAME)-boot.service
	rm $(SYSTEMD)/$(NAME)-stop.service
