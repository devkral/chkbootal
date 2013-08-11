#! /usr/bin/env python3

import os
import datetime
import shutil
import sys
import filecmp

#PYTHONOPTIMIZE=2

#####################################################
#variables
chkdir="/boot"
chksavedir="/var/chkboot"

####################################################
#helpmenu



helptext="""
### It is recommended to reboot after fixing the issue ###

 Choose action:
 NR: Nuke chkdir and restore the previous state (last shutdown). Reboot afterwards.
 NB: Nuke chkdir and restore the previous state (last shutdown) but
       make backupfiles of the current state. Reboot afterwards
 NNR: Nuke chkdir and restore the previous state (last shutdown) but don't reboot.
 R: Reboot
 C: Recheck and output corrupted files
 B: Backup old files
 quit/exit: Quit and continue boot !!!not recommended except after a syscrash after changes in chkdir!!!
 help/--help: this help menu
"""
# MD: Try to mount checkdir


#####################################################
#### directories and conversions ####


#dir which is checked
def chkdir_real(filee):
  return os.path.join(chkdir,filee)
def chkdir_virt(filee):
  return os.path.relpath(filee,chkdir)

#dir where reference files are stored
def chksavedir_real(filee):
  return os.path.join(chksavedir+os.sep+"save",filee)
def chksavedir_virt(filee):
  return os.path.relpath(filee,chksavedir+os.sep+"save")

#dir where backuped files are stored
def chkbackupdir():
  backupdate = datetime.datetime.now()
  backdir_=chksavedir+os.sep+"backup"+os.sep+repr(backupdate.year)+"-"+repr(backupdate.month)+"-"\
  +repr(backupdate.day)+"_"+repr(backupdate.hour)+"-"+repr(backupdate.minute)+"-"+repr(backupdate.second)
  return backdir_


def reboot():
  os.system("/usr/bin/systemctl reboot")

def less(inp):
  os.system("echo \""+inp+"\" | less")
	
#####################################################
#### housekeeping  ####



#remove old entries
def cleanold():
  try:
  
    for root, dirs, files in os.walk(chksavedir_real(""),False):
      for filee in files:
        virtfile=chksavedir_virt(os.path.join(root,filee))
        if os.path.exists(chkdir_real(virtfile)) == False:
          try:
            os.remove(chksavedir_real(virtfile))
          except OSError:
            print("OSError")
            return -1
        for dirr in dirs:
          try:
            os.rmdir(chksavedir_real(virtfile))
          except OSError:
            pass
          #print("Debug: Directory not empty")
  except FileNotFoundError:
    pass
  return 0


def check_chkdir():
  returnn = [True]
  try:
    for root, dirs, files in os.walk(chkdir_real(""),False):
      for filee in files:
        virtfile=chkdir_virt(os.path.join(root,filee))
        if os.path.exists(chksavedir_real(virtfile)) == False:
          returnn[0]=False
          returnn.append((chkdir_real(virtfile),"added"))
        else:
          try:
            if filecmp.cmp(chkdir_real(virtfile), chksavedir_real(virtfile),False) == False:
              returnn[0]=False
              returnn.append((chkdir_real(virtfile),"corrupted"))
          except PermissionError:
            returnn[0] = False
            returnn.append((chkdir_real(virtfile),"no permission"))
  except PermissionError:
    print ("No permission to access chkdir ("+chkdir_real("")+")")
    sys.exit(1)
  except FileNotFoundError:
    print ("chkdir not found")
    sys.exit(1)
  return returnn

#backupfolder re-creation; todo: maybe rsync-like behaviour would be useful
def update_chksavedir():
  temp=check_chkdir()
  if temp[0] != True:
    try:
      shutil.rmtree(chksavedir_real(""))
    except IOError:
      print("Debug: Save directory doesn't exist")
    except OSError:
      print("Debug: Save directory doesn't exist")
    try:
      shutil.copytree(chkdir_real(""), chksavedir_real(""), True)
    except IOError:
      print ("Reading save failed (Permission?)")
      return -1
    except OSError:
      print ("Reading save failed (Permission?)")
      return -1
    return 0
  else:
    return 0
	
def backupold():
  backdir=chkbackupdir()
  try:
    shutil.copytree(chkdir_real(""), backdir)
  except IOError:
    print ("Backup failed (missing permissions?)")
    return -1
  except OSError:
    print ("Backup failed (missing permissions?)")
    return -1
  print("Backup succeeded")
  return 0
	


#destroy former directory and re-copy

def nuke():
  try:
    shutil.rmtree(chkdir_real(""))
  except IOError:
    print("Can't delete, return")
    return -1
  try:
    shutil.copytree(chksavedir_real(""), chkdir_real(""))
  except IOError:
    print("bad error: can't restore")
    return -1
	
def nukebackup():
  if backupold() == 0:
    if nuke() == 0:
      return 0
    else:
      print ("Nuke failed, missing permissions?")
  else:
    print("Backup failed, don't nuke")
  return 1
   
        
		
#####################################################
#menu



def checkfailmenu():
  userinp=input(helptext)
  if userinp == "NR":
    if nuke()==0:
      reboot()
    else:
      checkfailmenu()
  elif userinp == "NB":
    if nukebackup()==0:
      reboot()
    else:
      checkfailmenu()
  elif userinp == "NNR":
    nuke()
    checkfailmenu()
  elif userinp == "R":
    reboot()
  elif userinp == "B":
    backupold()
    checkfailmenu()
  elif userinp == "C":
    returnn=check_chkdir()
    if returnn[0]==True:
      print ("All files are correct now. Reboot?")
      checkfailmenu()
    else:
      tempout="Corrupted files:\n"
      for elem in returnn[1:]:
        tempout+=elem[0]+" "+elem[1]+"\n"
      less(tempout)
      checkfailmenu()      
  elif userinp=="quit" or userinp=="quit()" or userinp=="exit" \
or userinp=="exit()":
    return 0
  elif userinp == ("help", "--help"):
    print("help:")
    checkfailmenu()
  else:
    checkfailmenu()
    return -1




#########################################################
#main part
argv=""
try:
  argv=sys.argv[1]
except IndexError:
  print("argument needed")

if argv == "check" or argv == "boot":
  returnn=check_chkdir()
  if returnn[0]==False and len(returnn)>1:
    tempout="Corrupted files:\n"
    for elem in returnn[1:]:
      tempout+=elem[0]+" "+elem[1]+"\n"
    print(tempout)
    checkfailmenu()
  else:
    print("Check successful")
elif argv == "save" or argv == "shutdown":
  update_chksavedir()
  cleanold()
elif argv == "test":
  checkfailmenu()
else:
  print("check: compare chkdir ("+chkdir+") against chksavedir/save ("+chksavedir+"/save)\nsave: update chksavedir")

sys.exit(0)
