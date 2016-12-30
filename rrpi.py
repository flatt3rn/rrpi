#Dependencies:
#	- Livestreamer (sudo apt-get install livestreamer)

import commands
import subprocess
import threading
import time
import SocketServer
import os
import urllib2
import datetime
import pygame

####
###
#Set this to 1 if you want to see the IP Adress at the screen until your first connection. If not set it to 0
Show_IP = 1
#Change this to the common IP of your Raspberry Pi. If its connected with this ip the ip is not shown at the screen
Reg_IP = "192.168.1.101"
#If you have a different home path
path_home = "/home/pi/"
###
####

sc = ""
donesomething = 0
C_IP = ""
C_PORT = 5563
C_BUFFER = 4096
base_path = "/usr/lib/rrpi/"
url_rip_program = 1
url_streamtxt = "https://raw.githubusercontent.com/flatt3rn/rrpi/master/streamtxt"
# 0: youtube-dl
# 1: livestreamer

def get_local_IP():
	#Try to connect for 10 minutes
	for i2 in range(0,200):
		#Get the Local IP Adress
		iflist = commands.getoutput("/sbin/ifconfig")
		for i1 in iflist.splitlines():
			if "inet " in i1:
				temp = i1.split(":")[1].split(" ")[0]
				if temp != "127.0.0.1":
					return temp
		time.sleep(3)
	return "none"

def get_audio_link(url):
	#Grab the Audio Links out of Youtube Videos. This feature is still in here but i dont use it
	audio_url = commands.getoutput(base_path + "bin/youtube-dl -f webm -g " + url)
	return audio_url

def get_video_link(url):
	#Grab Stream Link with youtube-dl (support more videos)
	if url_rip_program == 0:
		print "0 used"
		video_url = commands.getoutput(base_path + "bin/youtube-dl -f mp4 -g " + url)
	
	#Grab Stream Link with livestreamer (faster)
	if url_rip_program == 1:
		print "1 used"
		video_url_a = commands.getoutput("sudo /usr/bin/livestreamer --stream-url " + url + " best --yes-run-as-root").split(" ")
		video_url = video_url_a[len(video_url_a) - 1]
	
	#Needed if there is some other output beside the link
	if not video_url.startswith("http"):  
		video_url_a = video_url.split("http")
		video_url = ""
		for i1 in range(1,len(video_url_a)):
			video_url += "http" + video_url_a[i1]
	print video_url
	return video_url

#Interprets a txt file to read different streams.
#Implemented this to update stream pages without touching the script
def getStreamfromtxt(cmd,var):
	request = urllib2.Request(url_streamtxt)	
	response = urllib2.urlopen(request)
	page = response.read()
	cmds1 = page.split("%%&&%%\n")
	for i1 in cmds1:
		if i1.startswith(cmd):
			page = ""
			svar = ""
			cmds2 = i1.splitlines()[1:]
			for i2 in range(0, len(cmds2)):
				if cmds2[i2].split("%%/%%")[0] == "getpage":
					request = urllib2.Request(cmds2[i2].split("%%/%%")[1].replace("%%var%%",var).replace("%%svar%%",svar))	
					response = urllib2.urlopen(request)
					page = response.read()
				if cmds2[i2].split("%%/%%")[0] == "getpage2":
					os.system("wget " + cmds2[i2].split("%%/%%")[1].replace("%%var%%",var).replace("%%svar%%",svar) + " -O /tmp/streamgetpage -q")
					page = open("/tmp/streamgetpage").read()			
				if cmds2[i2].split("%%/%%")[0] == "checklines":
					for i3 in page.splitlines():
						if cmds2[i2].split("%%/%%")[1] in i3:
							svar = i3
							break;
				if cmds2[i2].split("%%/%%")[0] == "splitsvar":
						svar = svar.split(cmds2[i2].split("%%/%%")[1])[int(cmds2[i2].split("%%/%%")[2])]
				if cmds2[i2].split("%%/%%")[0] == "splitpage":
						svar = page.split(cmds2[i2].split("%%/%%")[1])[int(cmds2[i2].split("%%/%%")[2])]
				if cmds2[i2].split("%%/%%")[0] == "return":
					return svar
	
def change_ripper(value):
	#Change the Ripper remotely
	global url_rip_program
	url_rip_program = value

#Connection to the omxplayer is established here
class streamThread(threading.Thread):
	def __init__(self, url):
		threading.Thread.__init__(self)
		self.url = url

	def run(self):
		global sc
		#omxplayer started with the streamlink
		p = subprocess.Popen(['/usr/bin/omxplayer', '-o', 'hdmi', self.url], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		while 1:
			if sc == "p":
				#pause
				p.stdin.write('p')
				sc = ""
			elif sc == "r":
				#forward 30 sec
				p.stdin.write('\e[C')
				sc = ""
			elif sc == "l":
				#back 30 sec
				p.stdin.write('\e[D')
				sc = ""
			elif sc == "rr":
				#forward 10 min
				p.stdin.write('\e[A')
				sc = ""
			elif sc == "ll":
				#back 10 min
				p.stdin.write('\e[B')
				sc = ""
			elif sc == "vu":
				#volume up
				p.stdin.write('+')
				sc = ""
			elif sc == "vd":
				#volume down
				p.stdin.write('-')
				sc = ""
			elif sc == "q":
				#quit
				p.stdin.write('q')
				sc = ""
				break
			time.sleep(0.2)

#Start Stream Thread
def create_Thread(url):
	global td
	td = streamThread(url)
	td.start()

#Read all Files in the predefined Directory
def read_Directory(folder):
	if folder == "%%home%%":
		folder = path_home
	stxt = "c" + folder
	folderlist = os.walk(folder).next()[1]
	filelist = os.walk(folder).next()[2]
	folderlist.sort()
	filelist.sort()
	directory = []
	#Create a string with the whole folder content seperated by folders and files
	for i1 in folderlist:
		if not i1.startswith("."):
			stxt += "%%/%%d" + i1
	for i1 in filelist:
		if not i1.startswith("."):
			stxt += "%%/%%f" + i1
	if len(stxt) > 0:
		stxt = stxt + "\n"
		return stxt
	else:
		return ""

def set_background(path):
	global C_IP,donesomething
	if Show_IP == 1 and C_IP != Reg_IP:
		#If IP is not the regular one it displays the ip until the first connection
		pygame.init()
		pygame.mouse.set_visible(0)
		screen = pygame.display.set_mode((1280, 720))
		clock = pygame.time.Clock()
		font = pygame.font.SysFont("comicsansms", 200)
		text = font.render(C_IP, True, (200, 0, 30))
		while not donesomething:    
			#print donesomething
			screen.fill((255, 255, 255))
			screen.blit(text,(640 - text.get_width() // 2, 360 - text.get_height() // 2))
			pygame.display.flip()
			clock.tick(60)	
		pygame.quit()
	#This prints the standard image
	os.system("sudo " + base_path + "bin/fbi -T 1 " + path + " -noverbose")

#This provides the tcp connection
class TCP_Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		t_url = ""
		global sc,donesomething
		print "Connected: " + self.client_address[0]
		data = self.request.recv(C_BUFFER).strip()
		donesomething = 1
		#processing of the commands
		while data != "":
			try:      
				if len(data) > 3 and not data.startswith("rd_"):
					print data
					if 'td' in globals():
						sc = "q"
						while td.isAlive():
							time.sleep(0.2)
						sc = ""
					if data.startswith("ya_"):
						t_url = get_audio_link(data[3:])
					elif data.startswith("yv_"):
						t_url = get_video_link(data[3:])
					elif data.startswith("dl_"):
						t_url = data[3:]
					elif data.startswith("bg_"):
						if data[3:4] == "0":
							set_background(base_path + "images/raspi_standard.jpg")
					elif data.startswith("str_"):
						t_url = getStreamfromtxt(data[4:6],data[6:])
					elif data.startswith("fs_"):
						t_url = data[3:]
					if str(t_url) != "None":
						create_Thread(t_url)
				elif data == "re" and 'td' in globals():
					sc = "q"
					while td.isAlive():
						time.sleep(0.2)
					sc = ""
					create_Thread(t_url)
				elif data.startswith("rd_"):
					dircon = read_Directory(data[3:])
					if len(dircon) > 1:
						self.request.send(dircon)
					else:
						self.request.send("%%emtpy%%")	
				elif data.startswith("cr"):
					change_ripper(int(data[2:]))
					sc = ""
				elif data == "gd":
					os.system("sudo /sbin/shutdown -h 0")
					sc = ""
				elif data == "gr":
					os.system("sudo /sbin/shutdown -r 0")
					sc = ""
				elif len(data) > 0:
					sc = str(data)
				data = self.request.recv(C_BUFFER).strip()
			except IndexError as myerror:
				print "Shit Happens"
				break

def start_TCPServer():
	SocketServer.TCPServer.allow_reuse_address = True
	c_server = SocketServer.TCPServer((C_IP, C_PORT), TCP_Handler)
	c_server.serve_forever()

def mainstuff():
	global C_IP
	C_IP = get_local_IP()
	if C_IP == "none":
		exit()
	print C_IP + ":" + str(C_PORT)
	#Used a Thread so the script does not stuck there
	bgt = threading.Thread(target=set_background,args = (base_path + "images/raspi_standard.jpg",))
	bgt.start()
	start_TCPServer()

mainstuff()

