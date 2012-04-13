#! /bin/sh
# heise script extended by alex
# Original author: ju (ju at heisec dot de)
# 
# License: GPLv2 or later

chkdir="/boot"
chkdir_sed="\/boot\/"
savedir="/var/chkboot/checkfiles"
bootback="/var/chkboot/boot_backup"
adpath=""
file_current=""
adjust_path()
{
adpath="$savedir/$(echo "$file_current" | sed "s/$chkdir_sed//").chk"
mkdir -p "$(echo "$adpath" | sed -e "s/\([^ ]*\)\/[^ ]*/\1/")"

}

rm -R $savedir/*.chk
rm -R $bootback
mkdir -p $bootback
cp -R $chkdir/* $bootback/

cd $chkdir
files=$(find $chkdir -xdev -type f | grep -v "lost+found" | grep -v "Trash")
## refactor
files=$(echo $files)
for file_current in $files; do
adjust_path
sha512sum -b $file_current > "$adpath"
done

