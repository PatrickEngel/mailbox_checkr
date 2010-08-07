#!/usr/bin/env python

"""
mbox_checkr is a *simple* Mailbox Check Script.

Copyright (C) 2010  Patrick C. Engel

"""

import os
import gtk, gobject
import poplib, imaplib, email
from email.Utils import parsedate
from email.header import decode_header
from datetime import datetime
import base64
import sys
import ConfigParser
# import pynotify

__author__ = "Patrick C. Engel <info@pc-e.org>"
__date__ = "06 August 2010"

# __version__ = "$Revision$"

# ******************* mailbox config *******************

def get_default_confval(section, key, default):
	try:
		ret = config.get(section, key)
	except (ConfigParser.NoSectionError,ConfigParser.NoOptionError), e:
		ret = default
	return ret


config = ConfigParser.ConfigParser()

configdir = './'
configname = 'mailbox.cfg'
configpath = os.path.join(configdir, configname)
	
config.read(configpath)

protocol = config.get("mailbox1", "type") # "pop3"
server = config.get("mailbox1", "server") # "pop3.domain.com"
port = config.get("mailbox1", "port") # 110
login = config.get("mailbox1", "login") # "webmaster@domain.com"
passwd = config.get("mailbox1", "passwd") # "your-password"
ssl = config.getboolean("mailbox1", "ssl") #  0|1, yes|no
interval = int(get_default_confval('mailbox1', 'timeout', 20))


## check number of emails (num), and sum of new Mails (status)
#
#  @return num,status
def check_emails():
	if protocol == "pop3":
		if ssl:
			mailer = poplib.POP3_SSL(server, int(port))
		else:
			mailer = poplib.POP3(server, int(port))
		mailer.user(login)
		mailer.pass_(passwd)
	
		# mailer.list returns the email list
		status = mailer.stat()
		num = int(status[0])
		# print num
		# recent should set by: num_saved - num
		recent = 0
		mailer.quit()
		return num,recent
	
	elif protocol == "imap":
		if ssl:
			mailer = imaplib.IMAP4_SSL(server, int(port))
		else:
			mailer = imaplib.IMAP4(server, int(port))
		
		mailer.login(login, passwd)
		
		num = int(mailer.select()[1][0])
		
		mailer.close()
		mailer.logout()
		
		# print num
		return num,mailer.recent()[1][0]
		
	# InvalidArgException(Protocol not supported)
	raise ValueError("Protocol (type) "+protocol+" not supported")



# ******************* MBoxCheckr *******************

class MBoxCheckr(gtk.StatusIcon):
	def __init__(self, timeout):
		gtk.StatusIcon.__init__(self)
		menu = '''
			<ui>
			<menubar name="Menubar">
			<menu action="Menu">
			<menuitem action="MarkAllAsRead"/>
			<separator/>
			<menuitem action="About"/>
			<separator/>
			<menuitem action="Quit"/>
			</menu>
			</menubar>
			</ui>
		'''
		actions = [
			('Menu',  None, 'Menu'),
			('MarkAllAsRead', gtk.STOCK_OK, '_Mark all as Read', None, 'Mark all Mails as Read for MailBoxCheckr', self.on_mark_all_read),
			('About', gtk.STOCK_ABOUT, '_About...', None, 'About MBoxCheckr', self.on_about),
			('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit', self.on_quit)]
		ag = gtk.ActionGroup('Actions')
		ag.add_actions(actions)
		self.manager = gtk.UIManager()
		self.manager.insert_action_group(ag, 0)
		self.manager.add_ui_from_string(menu)
		self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent
		self.set_from_stock(gtk.STOCK_NO)
		self.set_blinking(True)
		self.set_tooltip('MBoxCheckr')
		self.set_visible(True)
		self.connect('activate', self.on_activate)
		self.connect('popup-menu', self.on_popup_menu)
		# initialise self.counter
        	try:
			self.counter = config.get("mailbox1", "total")
		except (NoSectionError, NoOptionError), e:
			self.counter = 0
		# register a periodic timer
		gobject.timeout_add_seconds(timeout, self.callback)

	def writeTotalMails(self, total):
		config.set('mailbox1', 'total', total)
		# Writing total to our configuration file
		configfile = open(configpath, 'wb')
		config.write(configfile)
	
	def callback(self):
		num,status = check_emails()
		self.set_blinking(False)
		if (self.counter==0):
			self.counter=int(num)
		else:
			if (int(self.counter) < int(num)):
				self.set_from_stock(gtk.STOCK_YES)
				self.counter=int(num)
		statustext = "%d messages" % int(num)
		self.set_tooltip(statustext)
		return True
	
	def on_mark_all_read(self, data):
		self.writeTotalMails(self.counter)
		self.counter=0
		self.set_from_stock(gtk.STOCK_NO)


	def on_popup_menu(self, status, button, time):
		self.menu.popup(None, None, None, button, time)
		
	
	def on_activate(self, data):
		self.on_about(data)


	def on_quit(self, data):
		gtk.main_quit()


	def on_about(self, data):
		dialog = gtk.AboutDialog()
		dialog.set_name('MBoxCheckr')
		dialog.set_version('1.0.0')
		dialog.set_comments('a simple Mailbox Watchdog')
		dialog.set_website('http://pc-e.org/')
		dialog.set_position(gtk.WIN_POS_CENTER)

		dialog.run()
		dialog.destroy()


def setup_app(*args):
	MBoxCheckr(interval)
		
def show_splash():

	splash = gtk.Window() 
	splash.set_decorated(False)
	splash.set_app_paintable(True)
	splash.realize()
	# splash xpm image
	iconsdir = './'
	imagename = 'mboxcheckr.xpm'
	path = os.path.join(iconsdir, imagename)
	pixmap, mask = gtk.gdk.pixmap_create_from_xpm(splash.window, None, path)
	width, height = pixmap.get_size()
	splash.resize(width, height)
	splash.window.set_back_pixmap(pixmap, False)
	del pixmap
	splash.set_position(gtk.WIN_POS_CENTER)

	splash.show()
	# ensure it is rendered immediately
	while gtk.events_pending():
		gtk.main_iteration()
	
	gobject.timeout_add(4000, splash.hide)
	gobject.idle_add(setup_app)


if __name__ == '__main__':
	show_splash()
	gtk.main()

