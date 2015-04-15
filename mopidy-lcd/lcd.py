from __future__ import unicode_literals

from math import ceil
from mpd import MPDClient
from time import sleep
import socket, os
import time

from lcdScroll import Scroller





class Background:
		#char 6 = currentPlayState

	def frame1():
			##FRAME 1
		self.lcd.create_char(1, [7,9,17,28,28,17,9,7]) #CasseteFrame0101
		self.lcd.create_char(2, [28,18,17,7,7,17,18,31]) #CasseteFrame0102
		self.lcd.create_char(3, [7,9,17,28,28,17,9,31]) #CassetteFrameR0101
		self.lcd.create_char(4, [28,18,17,7,7,17,18,28]) #CassetteFrameR0102
		self.lcd.create_char(5, [0,0,0,0,0,0,0,31]) #CasseteTapeFrame02

	
	def frame2():
			##FRAME 2
		self.lcd.create_char(1, [7,12,30,16,16,30,12,7]) #CasseteFrame0201
		self.lcd.create_char(2, [28,6,15,1,1,15,6,31]) #CasseteFrame0202
		self.lcd.create_char(3, [7,12,30,16,16,30,12,31]) #CassetteFrameR0201
		self.lcd.create_char(4, [28,6,15,1,1,15,6,28]) #CassetteFrameR0202
		self.lcd.create_char(5, [0,0,0,0,0,0,0,31]) #CasseteTapeFrame02
		
		
	def __init__(self, lcd):
		self.client = MPDClient()
		self.lcd = lcd
		self.scroller = Scroller()
		#Creating custom characters for display and loading them into memory

		self.lcd.create_char(2, [0, 14, 21, 23, 17, 14, 0, 0]) #Watch


		self.lcd.create_char(5, [31,17,10,4,10,17,31,0]) #Sand watch
		self.lcd.create_char(6, [0,27,14,4,14,27,0,0]) #X-Sign

		#Loading variables
		self.repeat = 0
		self.random = 0
		self.playlists = []
		self.listVal = 0
		self.playstatus = "stop"
		self.changeVolume = False
		self.screen = "clock"
		self.reconnect = False
		self.artist = "NONE"
		self.lastplayed = "null"
		self.title = "NONE"
		self.timeElapsed = "00:00"
		self.timeTotal = "00:00"
		self.playbackStatus = "stop"
		self.volume = 0
		self.updateTrack = True
		self.updateState = True
		self.updateTime = True
		self.nothingplaying = True
		self.pauseScreen = True
		self.scrollon = True

	
	#function to get local IP (not working if no internet connection)
	def get_ip(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('google.com', 0))
		ip = s.getsockname()[0]
		s.close()
		return ip
		
	def refresh_mpd(self):
		if self.screen == "main":
			if self.reconnect:
				self.reconnect_mpd()
			elif self.reconnect == False:
				connection = False
				try:
					self.status = self.client.status()
					self.song = self.client.currentsong()
					connection = True
					self.parse_mpd()
				except Exception as e:
					connection = False
					self.status = "NONE"
					self.song = "Stop"
				if connection == False:
					try:
						if e.errno == 32:
							self.reconnect = True
						else:
							print "Nothing to do"
					except Exception, e:
						self.reconnect = True
			
	def reconnect_mpd(self):
		client = MPDClient()
		client.timeout = 10
		client.idletimeout = None
		connection = False
		self.lcd.set_color(0.0,0.0,1.0)
		self.write("Connecting, \x05\nplease wait...")
		while connection == False:
			try:
				client.connect("localhost", 6600)
				connection=True
			except Exception, e:
				print e
				self.write("\x06ERROR\x06       \nCheck connection!")
				connection=False
				self.lcd.set_color(1.0,0.0,0.0)

		self.client = client
		self.reconnect = False
		self.lcd.set_color(1.0,1.0,1.0)
		self.lcd.create_char(6, [0, 31, 31, 31, 31, 31, 31, 0]) #Stop
		
	def parse_mpd(self):
	
		if self.screen == "main":
			try:
				artist = self.song["artist"].decode('utf-8')
				self.nothingplaying = False
			except:
				self.nothingplaying = True
				artist = "NONE"
			try:
				title = self.song["title"].decode('utf-8')
			except:
				title = "NONE"
			try:
				min = int(ceil(float(self.status["elapsed"])))/60
				min = min if min > 9 else "0%s" % min
				sec = int(ceil(float(self.status["elapsed"])%60))
				sec = sec if sec > 9 else "0%s" % sec
				timeElapsed = "\x02%s:%s" % (min,sec)
			except:
				timeElapsed = "\x0200:00-e"
			try:
				min = int(ceil(float(self.song["time"])))/60
				min = min if min > 9 else "0%s" % min
				sec = int(ceil(float(self.song["time"])%60))
				sec = sec if sec > 9 else "0%s" % sec
				timeTotal = "%s:%s" % (min,sec)
			except:
				timeTotal = "00:00"
			try:
				if self.status["state"] == "stop":
					playbackStatus = "\x06"
					self.lcd.create_char(6, [0, 31, 31, 31, 31, 31, 31, 0]) #Stop
				elif self.status["state"] == "play":
					playbackStatus = "\x06"
					self.lcd.create_char(6, [16,24,28,30,30,28,24,16])	#Play
					self.pause = False
				#	lastplayed = self.song["title"].decode('utf-8')
				elif self.status["state"] == "pause":
					playbackStatus = "\x06"
					self.lcd.create_char(6, [0,27,27,27,27,27,27,0]) #Pause
				else:
					playbackStatus = "({})".format(self.status["state"])

			except:
				playbackStatus = "\x06(error)"
			try:
				volume = int(self.status["volume"])
			except:
				volume = 0
			if self.artist != artist:
				self.artist = artist
				self.updateTrack = True
			if self.title != title:
				self.title = title
				self.updateTrack = True
			if self.timeElapsed != timeElapsed:
				self.timeElapsed = timeElapsed
				self.updateTime = True
			if self.playbackStatus != playbackStatus:
				self.playbackStatus = playbackStatus
				self.updateState = True
			if self.volume != volume:
				self.volume = volume
		
	def display(self):
		if self.screen == "clock":
			self.lcd.set_backlight(0)
			curTime = "Time: {}".format(time.strftime("%I:%M %p"))
			curDate = "{}".format(time.strftime("%b %d,%Y"))
			self.write("{:^16}\n{:^16}".format(curTime,curDate))
		elif self.screen == "begin":
			self.lcd.set_backlight(1)
			self.write("{:^16}\n{:^16}".format("Welcome to","MusicBox!"))
			self.lcd.set_color(1.0,0.0,0.0)
			sleep(0.5)
			self.lcd.set_color(0.0,1.0,0.0)
			sleep(0.5)
			self.lcd.set_color(0.0,0.0,1.0)
			sleep(0.5)
			self.lcd.set_color(1.0,1.0,1.0)
			sleep(2)
			self.reconnect_mpd()
			self.screen = "main"
		elif self.screen == "main":
			if self.updateTrack:
				self.updateTrack = False
				
				if self.nothingplaying:
					if self.changeVolume:
						self.lines = ["Nothing playing...", "{}{:>2}".format(self.timeElapsed,volume)]
					else:
						self.lines = ["Nothing playing", "{}{:>10}".format(self.timeElapsed,self.playbackStatus)]
				elif self.scrollon == False:
					self.lcd.clear()
					if self.changeVolume:
						self.lines = ["{} | {}".format(self.title,self.artist), "{}{:>10}".format(self.timeElapsed,volume)]
					elif self.timeElapsed == "00:00":
						self.lines = ["{} | {}".format(self.title,self.artist), "Loading Track {:>10}".format(self.playbackStatus)]
					else:
						self.lines = ["{} | {}".format(self.title,self.artist), "{}-{}{:>10}".format(self.timeElapsed,self.timeTotal,self.playbackStatus)]
				else:
					if self.changeVolume:
						self.lines = ["Title: {} - Artist: {}".format(self.title,self.artist), "{}{:>10}".format(self.timeElapsed,volume)]
					elif self.timeElapsed == "00:00":
						self.lines = ["{}".format(self.title), "Loading Track {:>10}".format(self.playbackStatus)]
					else:
						self.lines = ["Title: {} - Artist: {}".format(self.title,self.artist), "{}-{}{:>10}".format(self.timeElapsed,self.timeTotal,self.playbackStatus)]
				
				if self.scrollon:
					self.write("\n".join(self.lines))
					self.scroller.setLines(self.lines)
				else:
					
				#	self.write("\n".join(self.lines))
				#	self.scroller.setLines(self.lines)
					self.write(str(self.lines))
			else:
				if self.scrollon:
					self.lines = self.scroller.scroll()
					self.lines[1] = "{}{:>10}".format(self.timeElapsed,self.playbackStatus)
					self.write("\n".join(self.lines))
				else:
					self.lines[1] = "{}{:>10}".format(self.timeElapsed,self.playbackStatus)
					self.write("\n".join(self.lines))
		elif self.screen == "playlists":
			self.write("{:<16}\n{:<16}".format(self.playlists[self.listVal],self.playlists[self.listVal+1]))
		elif self.screen == "mopidySettings":
			self.write("{:^16}\n{:<6}{:^4}{:>6}".format("Mopidy Menu:","LOOP","","SHFLE"))
		elif self.screen == "shuffle":
			random = "Yes" if self.random == 1 else "No"
			self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Shuffle:","Yes",random,"No"))
		elif self.screen == "repeat":
			repeat = "Yes" if self.repeat == 1 else "No"
			self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Loop:","Yes",repeat,"No"))
		elif self.screen == "settings":
			self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Menu:","Audio","IP","Power"))
		elif self.screen == "display":
			self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Display:","White","Yellow","Blue"))
		elif self.screen == "scroll":
			if self.scrollon:
				self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Auto-Scroll",">On","","Off"))
			else:
				self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Auto-Scroll"," On","",">Off"))
				
		elif self.screen == "audio":
			self.write("{:^16}\n{:<5}{:^6}{:>5}".format("Audio:","HDMI","3.5J","Auto"))
		elif self.screen == "power":
			self.write("{:^16}\n{:<6}{:^4}{:>6}".format("Power:","OFF"," ","REBT"))
		elif self.screen == "ip":
			ipaddress = self.get_ip()
			self.write("IP Address:\n{:<16}".format(ipaddress))

	def button(self,dir):
		if self.screen == "clock":
			if dir == "Right":
				self.lcd.set_backlight(1)
				sleep(3)
				self.lcd.set_backlight(0)
			if dir == "Select":
				self.screen = "begin"
		elif self.screen == "main":
			if dir == "Left":
				if self.status["state"] == "play":
					self.client.pause()
					#playstatus = "pause"
				else:
					self.write(self.playbackStatus)
					self.client.play()
					#playstatus = "play"
			if dir == "Right":
				try:
				#	self.get_playlist()
					self.client.next()
				except:
					
					self.write("Nothing         \nto go to!             ")
					sleep(2)
			if dir == "Up":
				self.set_vol(5)
			if dir == "Down":
				self.set_vol(-5)
			if dir == "Select":
				try:
					self.write("{:16}\n{:16}".format("Loading","Playlists..."))
					self.get_playlist()
					self.screen = "playlists"
				except:
					self.write("NO PLAYLISTS\n                          ")
					sleep(3)
					self.screen = "mopidySettings"
		elif self.screen == "playlists":
			if dir == "Up":
				self.listVal = 0 if self.listVal >= len(self.playlists)-3 else self.listVal+2
			if dir == "Down":
				self.listVal = len(self.playlists)-2 if self.listVal < 0 else self.listVal-2
			if dir == "Left":
				self.load_playlist(self.playlists[self.listVal])
			if dir == "Right":
				self.load_playlist(self.playlists[self.listVal+1])
			if dir == "Select":
				self.screen = "mopidySettings"
		elif self.screen == "mopidySettings":
			if dir == "Right":
				self.screen = "shuffle"
			if dir == "Left":
				self.screen = "repeat"
			if dir == "Select":
				self.screen = "settings"
		elif self.screen == "shuffle":
			if dir == "Left":
				self.random = 1
			if dir == "Right":
				self.random = 0
			self.client.random(self.random)
			self.screen = "mopidySettings"
		elif self.screen == "repeat":
			if dir == "Left":
				self.repeat = 1
			if dir == "Right":
				self.repeat = 0
			self.client.repeat(self.repeat)
			self.screen = "mopidySettings"
		elif self.screen == "settings":
			if dir == "Left":
				self.screen = "audio"
			if dir == "Right":
				self.screen = "power"
			if dir == "Down":
				self.screen = "ip"
			if dir == "Select":
				self.screen = "display"
		elif self.screen == "audio":
			if dir == "Left":
				os.system("amixer cset numid=3 2")
			if dir == "Right":
				os.system("amixer cset numid=3 0")
			if dir == "Down":
				os.system("amixer cset numid=3 1")
			self.screen = "settings"
		elif self.screen == "display":
			if dir == "Left":
				self.lcd.set_color(1.0,1.0,1.0)
			if dir == "Down":
				self.lcd.set_color(1.0,1.0,0.0)
			if dir == "Right":
				self.lcd.set_color(0.0,0.0,1.0)
			if dir == "Select":
				self.screen = "scroll"
		elif self.screen == "scroll":
			if dir == "Left":
				self.scrollon = True
				self.updateTrack = True
			if dir == "Right":
				self.scrollon = False
				self.updateTrack = True
			if dir == "Select":
				self.lcd.clear()
				self.screen = "main"

		elif self.screen == "power":
			if dir == "Left":
				os.system("shutdown -h now")
				self.quit_nicely()
				self.screen = "settings"
			if dir == "Right":
				os.system("init 6")
				#self.quit_nicely()
				self.screen = "settings"
			if dir == "Select":
				self.screen = "settings"
		elif self.screen == "ip":
			self.screen = "settings"
			
	def set_vol(self,amount):
		self.changeVolume = True
		volume = int(self.volume) + int(amount)
		volume = 100 if volume > 100 else volume
		volume = 0 if volume < 0 else volume
		self.client.setvol(volume)
		self.changeVolume = False

		
	def write(self,info):
		self.lcd.set_cursor(0,0)
		self.lcd.message(info)
		
	def display_off(self):
		self.write("{:^16}\n{:^16}".format("Good","Bye!"))
		sleep(2)
		self.lcd.set_backlight(0)
		self.lcd.enable_display(False)
		
	def quit_nicely(self, *args):
		self.client.stop()
		self.display_off()
		exit(0)
	
	def get_playlist(self):
		for list in self.client.listplaylists():
			self.playlists.append(list['playlist'])
		if len(self.playlits) == 0:
			raise
	
	def load_playlist(self,item):
		self.client.clear()
		self.client.load(item)
		self.client.play()
		self.screen = "main"
	
	
		#sleep(0.5)
		#lcd.clear()
		#lcd.message("\n\x05\x01\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x06\x02")
		#sleep(0.5)
		#lcd.clear()
		#lcd.message("\n\x06\x02\x03\x04\x03\x04\x03\x04\x03\x04\x03\x04\x03\x04\x05\x01")
