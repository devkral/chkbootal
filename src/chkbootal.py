#! /usr/bin/python

import hashlib
import os
import datetime
import shutil
import sys
#import filecmp

#PYTHONOPTIMIZE=2

#####################################################
#lone variables
chkdir="/boot"
chksavedir="/var/chkboot"

####################################################
#helpmenu

#def helpnorm()
#	print("The file"++"in "+chkdir+" has changed.")  
#	print("Mark changed file and continue [y] (default) or panic [n] or ignore [i]?")





helppanic="""
 Choose action:
 NR: Nuke chkdir and restore the previous state (last shutdown). (Reboot afterwards)
 NB: Nuke chkdir and restore the state from the last shutdown but make backupfiles. (Reboot)
 NNR: Nuke chkdir and restore the state from the last shutdown. No reboot. For testing
 R: Reboot
 B: Backup old files
 CA: Check everything
 MD: Try to mount checkdir
 quit: Go back
 help/--help: this help menu
"""



#####################################################
#section for init

hashen=hashlib.new("sha512");


def chkdir_safe(filee):
	return os.path.realpath(chkdir+os.sep+filee)

def chksavedir_safe(filee):
	return os.path.realpath(chksavedir+os.sep+filee)
	
def chksavedirhash_safe(filee):
	return os.path.realpath(chksavedir_safe("")+os.sep+"chkfiles"+os.sep+filee)

def chksavedirhash_safe2():
	return os.path.realpath(chksavedir_safe("")+os.sep+"chkfiles"+os.sep)

#backdir_shut is useful more than once
def chksavedirbackupshut_safe(filee):
	return os.path.realpath(chksavedir_safe("")+os.sep+"backup"+os.sep+filee)

def shortfile(basedir,filee):
	return os.path.relpath(filee,basedir)
		


#def chkbackdir_safe():
#	return os.path.realpath(backdir_shut())+"/"+os.path.basename(chkdir_safe())

	
#####################################################
#section for functions




def hashfile(filee):
	try:
		hashobject=open(filee,"rb")
	except IOError:
		return -1
	hashen.update(hashobject.read())
	hashobject.close()
	return hashen.hexdigest()


#remove old entries
def cleanhash():
	for root, dirs, files in os.walk(chksavedirhash_safe(""),False):
		for filee in files:
			realfile=os.sep+shortfile(chksavedirhash_safe(""),os.path.join(root,filee))[:-4]
			if os.path.exists(realfile) == False:
				try:
					os.remove(os.path.join(root,filee))
				except OSError:
					print("OSError")
					return -1
		for dirr in dirs:
			 try:
			 	os.rmdir(os.path.join(root,dirr))
			 except OSError:
			 	None
			 	#print("Debug: Directory not empty")
			
		
	return 0

#check hash normal
def checkhash():
	returnn =[0]
	
	for root, dirs, files in os.walk(chkdir_safe("")):
		for filee in files:
			try:
				testobject=open(chksavedirhash_safe(os.path.join(root,filee))+".chk")
			except IOError:
				returnn[0]=1
				returnn.append(os.path.join(root,filee))
			
			else:
				if hashfile(os.path.join(root,filee)) == testobject.read():
					testobject.close()
				else:
					testobject.close()
					returnn[0]=1
					returnn.append(os.path.join(root,filee))		
			
	return returnn


		
def checkhash_backup():
	returnn =[0]
	for root, dirs, files in os.walk(chksavedirbackupshut_safe("")):
		for filee in files:
			checkfile=chksavedirhash_safe("")+os.sep+shortfile(chksavedirbackupshut_safe(""),os.path.join(root,filee))+".chk"
			try:
				testobject=open(checkfile)
			except IOError:				
				returnn[0]=1
				returnn.append(os.path.join(root,filee))
	
			else:
				if hashfile(os.path.join(root,filee)) == testobject.read():
					testobject.close()
				else:
					testobject.close()
					returnn[0]=1
					returnn.append(os.path.join(root,filee))		
			
	return returnn
				

def createhash():
	if cleanhash()==0:
		for root, dirs, files in os.walk(chkdir_safe(""),False):
			for filee in files:	
				temphash=hashfile(os.path.join(root,filee))
				if temphash != -1:
					if os.path.exists(chksavedirhash_safe(root)) == False:
						try:
							os.makedirs(chksavedirhash_safe(root),0o700)
						except OSError as e:
							print(e)
							return -1
					try:
						createobject=open(chksavedirhash_safe(os.path.join(root,filee))+".chk","w")
					except IOError as e:
						return -1
					createobject.write(temphash)
					createobject.close()
				else:
					return temphash
		return 0
	else:
		return -1


## backup functions
	
def backupold():
	backupdate = datetime.datetime.now()
	backdir_sof=os.path.normpath(chksavedir)+os.sep+"backupold-("+repr(backupdate.year)+"-"+repr(backupdate.month)+"-"\
	+repr(backupdate.day)+"_"+repr(backupdate.hour)+"-"+repr(backupdate.minute)+"-"+repr(backupdate.second)+")"
	try:
		shutil.copytree(chkdir_safe(""), backdir_sof)
	except IOError:
		return -1
	except OSError:
		return -1
	return 0

#backupfolder re-creation; todo: maybe rsync-like behaviour would be useful
def backupshutdown():
	temp=checkhash_backup()
	if temp != 0:
		try:
			shutil.rmtree(chksavedirbackupshut_safe(""))
		except IOError: #can fail
			print("Debug: backup directory missed")
		except OSError: #can fail
			print("Debug: backup directory missed")
	
		try:
			shutil.copytree(chkdir_safe(""), chksavedirbackupshut_safe(""), True)
		except IOError:
			print ("backup failed")
			return -1
		except OSError:
			print ("backup failed")
			return -1
		return 0
	else:
		return 0
	


#destroy former directory and re-copy

def nuke():
	try:
		shutil.rmtree(chkdir_safe(""))
	except IOError:
		return -1
	try:
		shutil.copytree(chksavedirbackupshut_safe(""), chkdir_safe(""))
	except IOError:
		print("bad error: can't restore")
		return -1
	
	
def nukebackup():
	if backupold() == 0:
		if nuke() != 0:
			print("error: can't nuke")
			return 1
		
		
#####################################################
#panicoptions



def panicoptions():
	#get user input and translate it via if else because of missing switch
	userinp=input(helppanic)
	if userinp == "NR":
		nuke()
	elif userinp == "NB":
		nukebackup()
	elif userinp == "NNR":
		nuke()
	elif userinp == "R":
		print("reboot")
	elif userinp == "B":
		backupold()
	elif userinp == "CA":
		returnn=checkhash()
		if returnn[0]==0:
			print("checkdir ok")
		else:
			print("hash dismatches in checkdir:\n"+returnn[0:])
		returnn2=checkhash_backup()
		if returnn2[0]==0:
			print("backup directory ok")
		else:
			print("hash dismatches in the backup directory:\n"+returnn2[0:])
		
	elif userinp == "MD":
		print("mount checkdir")
	elif userinp == "quit" or userinp == "quit()":
		return 0
	elif userinp == ("help", "--help"):
		print("help:")
		panicoptions()
	else:
		panicoptions()
	return -1

#def panichelper():
#	os. ("systemctl start pythonhashpanic.service")




#####################################################
#section for functions working with panicoptions

	
def decodereturnn(getfilee):
	test=input(getfilee+" hasn't a valid hash. Press:\ny: for accepting the new hash,\nn: for the panic menu\ni: for ignoring the change\n")
	if test=="Y" or test=="y" or test=="yes" or test=="Yes" or test=="YES":
		temphash=hashfile(getfilee)
		if temphash != -1:
			if os.path.exists(chksavedirhash_safe(os.path.dirname(getfilee))) == False:
				try:
					os.makedirs(chksavedirhash_safe(os.path.dirname(getfilee)),0o700)
				except OSError as e:
					print(e)
					return -1
			try:
				createobject=open(chksavedirhash_safe(getfilee)+".chk","w")
			except IOError as e:
				print(chksavedirhash_safe(getfilee)+".chk")
				return -1
			createobject.write(temphash)
			createobject.close()
		return 0
	elif test=="N" or test=="n" or test=="no" or test=="No" or test=="NO":
		panicoptions()
	elif test=="i":
		return 0
	else:
		decodereturnn(getfilee)

def question_hash(returnn):
	for getfilee in returnn[1:]:
		decodereturnn(getfilee)
	
def checkdir():
	if os.path.isdir(chkdir_safe(""))==False:
		print ("chkdir invalid")
		return -1
		
	if os.path.isdir(chksavedir_safe(""))==False:
		print("error: no directory to save; create directory")
		try:
			os.makedirs(chksavedir_safe(""),0o744,false)
		except OSError:
			return -1
		try:
			os.mkdir(chksavedirbackupshut_safe(""),0o700)
		except OSError:
			print("error: previous directory creation has failed")
			return -1
		try:
			os.mkdir(chksavedirhash_safe2(),0o700)
		except OSError:
			print("error: chksavedirhash_safe2() has failed")
			return -1
		return 0
	else:
		try:
			os.chmod(chksavedir_safe(""), 0o744)
		except OSError as e:
			print(e)
	
	if os.path.isdir(chksavedirhash_safe2())==False:
		print("error: "+chksavedirhash_safe2()+" doesn't exist. This could be a hack. Have you deleted the directory accidentally?")
		if input("Type \"yes\" to recreate it otherwise panic") == "yes":
			try:
				os.mkdir(chksavedirhash_safe2(),0o700)
			except IOError:
				print("error: directory creation failed")
				return -1
			return 0
		else:
			panicoptions()
	else:
		try:
			os.chmod(chksavedirhash_safe2(), 0o700)
		except OSError as e:
			print(e)
			
	return 0


#why hash? we backup and there's a wonderful function to compare two directories
#def comparee_file():
#	if filecmp.cmpfiles(chkdir_safe(""), chkbackdir_safe("")) != True:
#		panicoptions()

#because hash is more interesting^^
def comparee():
	returnn=checkhash()
	if returnn[0] != 0:
		question_hash(returnn)


#########################################################
#main part
argv=""
try:
	argv=sys.argv[1]
except IndexError:
	print("argument needed")

if argv == "check" or argv == "boot":
	checkdir()
	comparee()

if argv == "save" or argv == "shutdown":
	checkdir()
	createhash()
	cleanhash()
	backupshutdown()

if argv == "--panic":
	panicoptions()

