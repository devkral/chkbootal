#! /bin/sh
# heise script extended by alex
# Original author: ju (ju at heisec dot de)
# 
# License: GPLv2 or later

chkdir="/boot"
chkdir_sed="\/boot\/"
savedir="/var/chkboot/checkfiles"
bootback="/var/chkboot/boot_backup"
bacdir="/var/chkboot/oldfiles_backup-$(date +"%y%m%d-%H%M")"
what=""
what_action=""
adpath=""
file_current=""
adjust_path()
{
adpath="$savedir/$(echo "$file_current" | sed "s/$chkdir_sed//").chk"

}

#don't confuse main loop for 2 nd loop
adpath2=""
file_current2=""
adjust_path2()
{
adpath2="$savedir$(echo "$file_current2" | sed "s/$chkdir_sed//").chk"

}


strange_change()
{
  echo "The file $what in $chkdir has changed."  
  echo "Mark changed file and continue [y] (default) or panic [n] or ignore [i]?"
  read what_action
  if [ "$what_action" = "" ] || [ "$what_action" = "y" ] || [ "$what_action" = "yes" ] || [ "$what_action" = "Yes" ]; then
    sha512sum -b $what > $adpath.modified
    return 0
  fi
## panic!!  
  if [ "$what_action" = "n" ] || [ "$what_action" = "no" ] || [ "$what_action" = "No" ]; then
    take_action
    return 0
  fi
  
  if [ "$what_action" = "i" ] || [ "$what_action" = "I" ]; then
    return 0
  fi
## re-ask
  strange_change
  
}

no_dir()
{
  echo "Directory $savedir doesn't exist!"
  echo "Create directory [y] (default) or panic [n]?"
  read what_action
  if [ "$what_action" = "" ] || [ "$what_action" = "y" ] || [ "$what_action" = "yes" ] || [ "$what_action" = "Yes" ]; then
    mkdir -p $savedir
    exit 0
  fi
## panic!!  
  if [ "$what_action" = "n" ] || [ "$what_action" = "no" ] || [ "$what_action" = "No" ]; then
    take_action
    return 0
  fi
  
## re-ask
  no_dir
}

help_menu()
{
  echo "Choose action:"
  echo "NR: Nuke $chkdir and restore the state from the last shutdown. REBOOT!"
  echo "NB: Nuke $chkdir and restore the state from the last shutdown but make backupfiles. REBOOT!"
  echo "NNR: Nuke $chkdir and restore the state from the last shutdown. No reboot. For testing"
  echo "R: Reboot"
  echo "B: Backup old files"
  #echo "R: Clean bootdir, reinstall grub and kernel, generate new shasum and reboot"
  echo "CK: Check if the kernel is affected"
  echo "CA: Check everything"
  echo "MD: Try to mount checkdir"
  #echo "D: Compare"
  echo "M: Manual repair: drop shell (I know bad idea)"
  echo "quit: Go back"
  echo "help/--help: this help menu"
}

## check files with linux or kernel in their name
check_kernel()
{
  cd $chkdir
  files2="$(find "$chkdir" -xdev -type f | grep -v "lost+found"  | grep -v "Trash" | grep -E "(linux|kernel)")"

## refactor
  files2=$(echo $files2)
  for file_current2 in $files2; do
  adjust_path2
   if [ "$(sha512sum -b $file_current2)" != "$(cat $adpath2 2> /dev/null)" ]; then
    echo "$file_current2 has a different checksum"
   fi
  done
  return
}

## check all files
check_all()
{
  cd $chkdir
  files2="$(find "$chkdir" -xdev -type f | grep -v "lost+found"  | grep -v "Trash")"

## refactor
  files2=$(echo $files2)
  for file_current2 in $files2; do
  adjust_path2
   if  [ "$(sha512sum -b $file_current2)" != "$(cat $adpath2 2> /dev/null)" ]; then
    echo "$file_current2 has a different checksum"
   fi
  done
  return
}

take_action()
{
  help_menu

  read what_action
#action
  
  if [ "$what_action" = "NR" ]; then
     rm -R $chkdir/*
     cp -R $bootback/* $chkdir
     if [ "$(check_all)" = "" ]; then
       reboot
     else
       echo "Still an error left"
     fi
     return 0
  fi
  
  if [ "$what_action" = "NB" ]; then
     mkdir -p $bacdir
     cp -R $chkdir/* $bacdir
     rm -R $chkdir/*
     cp -R $bootback/* $chkdir
     if [ "$(check_all)" = "" ]; then
       echo "Files are ok"
     else
       echo "Still an error left"
     fi
     return 0
  fi
  
  if [ "$what_action" = "NNR" ]; then
     rm -R $chkdir/*
     cp -R $bootback/* $chkdir
     if [ "$(check_all)" = "" ]; then
       reboot
     else
       echo "Still an error left"
     fi
     return 0
  fi
  
  if [ "$what_action" = "B" ]; then
     mkdir -p $bacdir
     cp -R $chkdir/* $bacdir
     take_action
     return 0
  fi
  
   
  if [ "$what_action" = "CK" ]; then
     if [ "$(check_kernel)" = "" ]; then
       echo "Kernel files are ok"
     fi
     take_action
     return 0
  fi
  
  if [ "$what_action" = "CA" ]; then
     if [ "$(check_all)" = "" ]; then
       echo "Files are ok"
     fi
     take_action
     return 0
  fi
  
  if [ "$what_action" = "MD" ]; then
     mount $chkdir
     take_action
     return 0
  fi
  
  if [ "$what_action" = "M" ]; then
     /bin/sh
     take_action
     return 0
  fi
    
  if [ "$what_action" = "R" ]; then
     reboot
     return 0
  fi
  
  if [ "$what_action" = "quit" ]; then
     return 0
  fi
  
  if [ "$what_action" = "help" ] || [ "$what_action" = "--help" ]; then
     take_action
     return 0
  fi
  
  echo "Invalid command"
  take_action
  return 0
}


[ ! -d $savedir ] && no_dir

cd $chkdir
files=$(find $chkdir -xdev -type f | grep -v "lost+found"  | grep -v "Trash")
## refactor
files=$(echo $files)
for file_current in $files; do
adjust_path
  if [ "$(sha512sum -b $file_current)" != "$(cat $adpath 2> /dev/null)" ]; then
   if [ -f $adpath.modified ] && [ "$(sha512sum -b $file_current)" = "$(cat $adpath.modified)" ]; then
    echo "shutdownsafe.sh hasn't saved $file_current"
   else
    what="$file_current"
    strange_change
   fi
  fi
done
