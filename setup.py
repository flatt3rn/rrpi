import os
import sys


def usage():
	print "Usage: sudo python setup.py [option]"
	print "\nOptions:\n	- install\n	- uninstall\n	- update [Not implemented]"


if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

if not len(sys.argv) == 2:
	usage()
	sys.exit()

pathname = os.path.dirname(sys.argv[0]) 
basepath = os.path.abspath(pathname)
cron = "@reboot	sudo /usr/bin/python /usr/lib/rrpi/rrpi.py"
if sys.argv[1] == "install":
	print "Create Folder: /usr/lib/rrpi"
	os.system("sudo mkdir /usr/lib/rrpi/")
	print "Copy ./rrpi.py to /usr/lib/rrpi.py"
	os.system("sudo cp " + basepath + "/rrpi.py /usr/lib/rrpi/rrpi.py")
	print "Copy ./bin to /usr/lib/rrpi/bin"
	os.system("sudo cp -r " + basepath + "/bin /usr/lib/rrpi/")
	print "Copy ./images to /usr/lib/rrpi/images"
	os.system("sudo cp -r " + basepath + "/images /usr/lib/rrpi/")
	print "Creating Crontab"
	os.system("sudo crontab -l > /tmp/crontab_save")
	t = open("/tmp/crontab_save").read()
	with open("/tmp/crontab_save", "a") as myfile:
		if not cron in t:
			myfile.write("\n" + cron + "\n")
	os.system("cat /tmp/crontab_save | sudo crontab -")
	
elif sys.argv[1] == "uninstall":
	print "Deleting /usr/lib/rrpi"
	os.system("sudo rm -r /usr/lib/rrpi")
else:
	usage()
	sys.exit()
print "Ready"
